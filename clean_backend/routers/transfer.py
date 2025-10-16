from decimal import Decimal
import os
from typing import Any, Dict, Optional
import uuid
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request
from fastapi import BackgroundTasks
from pydantic import BaseModel, condecimal
from sqlalchemy.orm import Session

from ..auth import get_current_user
from fastapi_auth0.auth import Auth0User
from ..database import get_db, SessionLocal
from ..models import User, BridgeCustomer, BridgeWallet, Transfer
from ..models import SendTransaction
from ..bridge import BridgeClient
from ..services.encumbrance_service import EncumbranceService, TREASURY_WALLET_ID, TREASURY_CUSTOMER_ID
from ..services.rate_service import rate_service
from ..models import PlaidItem
from ..services.bucket_heap import deduct_lowest_rates, add_to_rate_bucket
from ..services.bucket_heap import deduct_highest_rates

router = APIRouter(prefix="/transfers", tags=["transfers"])

# Separate router with no prefix to expose legacy /deposits endpoint at root
public_router = APIRouter(tags=["transfers"], include_in_schema=False)


# ---------------------------- Schemas ----------------------------
class DepositIn(BaseModel):
    amount: condecimal(gt=Decimal("0"), max_digits=18, decimal_places=2)
    external_account_id: str

class SendIn(BaseModel):
    recipient_user_id: UUID
    amount: condecimal(gt=Decimal("0"), max_digits=18, decimal_places=2)
    memo: Optional[str] = None
    speed_option: Optional[str] = "standard"

class QuoteOut(BaseModel):
    sender_currency: str
    recipient_currency: str
    amount_sent: float
    usdc_amount: float
    amount_received: float
    exchange_rate: float

class DepositOut(BaseModel):
    fiat_transfer_id: str
    usdb_transfer_id: str
    encumbrance_id: str
    state: str

class SendOut(BaseModel):
    transfer_id: str
    status: str
    sender_currency: str
    recipient_currency: str
    amount_sent: float
    amount_received: float
    exchange_rate: Optional[float] = None


class WithdrawalIn(BaseModel):
    amount: condecimal(gt=Decimal("0"), max_digits=18, decimal_places=2)
    external_account_id: str
    apply_profit_to_user: Optional[bool] = False

class WithdrawalPreviewOut(BaseModel):
    from_currency: str
    to_currency: str
    withdraw_amount: float
    developer_fee_percent: float
    expected_receive_amount: float
    buy_rate_used: Optional[float] = None


# ---------------------------- Helpers ----------------------------

Q2 = Decimal("0.01")
Q6 = Decimal("0.01")

def round_fiat(amount: Decimal) -> Decimal:
    return amount.quantize(Q2)

def round_usdc(amount: Decimal) -> Decimal:
    return amount.quantize(Q6)

def _get_user_by_sub(db: Session, sub: str) -> Optional[User]:
    """Look up user by Auth0 subject ID only - NEVER by email to prevent auth bugs"""
    return db.query(User).filter(User.auth0_id == sub).first()

def _get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def _deduct_from_buckets(fiat_balance_by_rate: Dict, amount: Decimal) -> Dict:
    """
    Deduct amount from fiat_balance_by_rate buckets using lowest-rate-first strategy (max profit)
    Returns updated buckets dict
    """
    if not fiat_balance_by_rate:
        raise ValueError("Insufficient balance: no buckets available")
    
    # Sort buckets by rate (ascending) to use lowest rates first
    sorted_buckets = sorted(fiat_balance_by_rate.items(), key=lambda x: float(x[0].split('_')[-1]) if '_' in x[0] else 0)
    
    remaining_amount = amount
    updated_buckets = fiat_balance_by_rate.copy()
    
    for rate_key, bucket_amount in sorted_buckets:
        if remaining_amount <= 0:
            break
            
        bucket_balance = Decimal(str(bucket_amount))
        deduct_amount = min(remaining_amount, bucket_balance)
        
        updated_buckets[rate_key] = float(bucket_balance - deduct_amount)
        remaining_amount -= deduct_amount
        
        # Remove empty buckets
        if updated_buckets[rate_key] <= 0:
            del updated_buckets[rate_key]
    
    if remaining_amount > 0:
        raise ValueError(f"Insufficient balance: need {amount}, only {amount - remaining_amount} available")
    
    return updated_buckets

def _add_to_bucket(fiat_balance_by_rate: Dict, rate_key: str, amount: Decimal) -> Dict:
    """Add amount to specific rate bucket"""
    updated_buckets = fiat_balance_by_rate.copy()
    current_amount = Decimal(str(updated_buckets.get(rate_key, 0)))
    updated_buckets[rate_key] = float(current_amount + amount)
    return updated_buckets


# ---------------------------- Routes ----------------------------

@router.post("/send", response_model=SendOut)
async def send_transfer(
    body: SendIn,
    db: Session = Depends(get_db),
    auth_user: Auth0User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None,
    request: Request = None,
):
    """
    Send money between users with proper currency conversion and rate locking.
    
    Handles two cases:
    1. Same currency send (H → H): Direct transfer with current rate locking
    2. Cross-currency send (C₁ → C₂): Convert via USDC with proper rate tracking
    """
    
    # Get sender
    sender = _get_user_by_sub(db, auth_user.id)
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")
    
    # Get recipient
    recipient = _get_user_by_id(db, body.recipient_user_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    # Get sender's bridge wallet (row lock to serialize concurrent sends)
    sender_wallet = (
        db.query(BridgeWallet)
        .with_for_update()
        .filter(BridgeWallet.user_id == sender.id)
        .first()
    )
    if not sender_wallet:
        raise HTTPException(status_code=400, detail="Sender wallet not found")
    
    # Get recipient's bridge wallet (row lock as well)
    recipient_wallet = (
        db.query(BridgeWallet)
        .with_for_update()
        .filter(BridgeWallet.user_id == recipient.id)
        .first()
    )
    if not recipient_wallet:
        raise HTTPException(status_code=400, detail="Recipient wallet not found")
    
    sender_currency = sender_wallet.fiat_currency or 'USD'
    recipient_currency = recipient_wallet.fiat_currency or 'USD'
    send_amount = body.amount
    
    # Get current rates for locking
    sender_rate = rate_service.get_usdc_rate(sender_currency)
    recipient_rate = rate_service.get_usdc_rate(recipient_currency)
    
    if sender_rate is None or recipient_rate is None:
        raise HTTPException(status_code=502, detail="Unable to fetch current exchange rates")
    
    # Create rate keys for bucket tracking
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    sender_rate_key = f"R_{timestamp}_{sender_rate}"
    recipient_rate_key = f"R_{timestamp}_{recipient_rate}"
    
    try:
        client = BridgeClient()
        # Idempotency: allow caller to supply an idempotency key, reuse for bundle id
        idem_key = None
        try:
            idem_key = request.headers.get("X-Idempotency-Key") if request else None
        except Exception:
            idem_key = None
        send_bundle_id = (
            uuid.uuid5(uuid.NAMESPACE_URL, idem_key) if idem_key else uuid.uuid4()
        )

        # If idempotent send already exists, short-circuit
        existing = None
        if idem_key:
            existing = db.query(SendTransaction).filter(SendTransaction.send_id == send_bundle_id).first()
        if existing:
            return SendOut(
                transfer_id=str(existing.send_id),
                status=existing.status,
                sender_currency=existing.sender_currency.upper(),
                recipient_currency=existing.recipient_currency.upper(),
                amount_sent=float(existing.sender_fiat_amount),
                amount_received=float(existing.recipient_fiat_amount),
                exchange_rate=float(existing.exchange_rate) if existing.exchange_rate else None,
            )
        if sender_currency.upper() == recipient_currency.upper():
            # Same-currency send (H → H)
            # Deduct from sender's buckets using highest-rate-first and compute USDC_locked
            updated, consumed, usdc_locked = deduct_highest_rates(
                sender_wallet.fiat_balance_by_rate or {}, send_amount
            )
            sender_wallet.fiat_balance_by_rate = updated

            # Credit recipient at current rate key
            recipient_wallet.fiat_balance_by_rate = add_to_rate_bucket(
                recipient_wallet.fiat_balance_by_rate or {}, recipient_rate, send_amount
            )

            # Compute live USDC to send and perform treasury adjustment BEFORE wallet-to-wallet send
            usdc_live = round_usdc(send_amount * sender_rate)
            usdc_locked_q = round_usdc(usdc_locked)
            delta = round_usdc(usdc_live - usdc_locked_q)  # >0 treasury→sender, <0 sender→treasury
            tsx = None
            if delta != 0:
                if delta > 0:
                    # Compensation: treasury → sender |Δ|
                    tsx = client.create_transfer_sync({
                        "amount": str(round_usdc(delta)),
                        "on_behalf_of": TREASURY_CUSTOMER_ID,
                        "client_reference_id": str(send_bundle_id),
                        "source": {
                            "payment_rail": "bridge_wallet",
                            "bridge_wallet_id": TREASURY_WALLET_ID,
                            "currency": "usdc"
                        },
                        "destination": {
                            "payment_rail": "solana",
                            "bridge_wallet_id": sender_wallet.wallet_id,
                            "currency": "usdc"
                        }
                    })
                else:
                    # Profit: sender → treasury |Δ|
                    tsx = client.create_transfer_sync({
                        "amount": str(round_usdc(abs(delta))),
                        "on_behalf_of": sender_wallet.customer_id,
                        "client_reference_id": str(send_bundle_id),
                        "source": {
                            "payment_rail": "bridge_wallet",
                            "bridge_wallet_id": sender_wallet.wallet_id,
                            "currency": "usdc"
                        },
                        "destination": {
                            "payment_rail": "solana",
                            "bridge_wallet_id": TREASURY_WALLET_ID,
                            "currency": "usdc"
                        }
                    })

            # Wallet-to-wallet (visible) transfer: sender → recipient (USDC_live)
            try:
                w2w = client.create_transfer_sync({
                    "amount": str(round_usdc(usdc_live)),
                    "on_behalf_of": sender_wallet.customer_id,
                    "client_reference_id": str(send_bundle_id),
                    "source": {
                        "payment_rail": "bridge_wallet",
                        "bridge_wallet_id": sender_wallet.wallet_id,
                        "currency": "usdc"
                    },
                    "destination": {
                        "payment_rail": "solana",
                        "bridge_wallet_id": recipient_wallet.wallet_id,
                        "currency": "usdc"
                    }
                })
            except Exception as w2w_err:
                # Compensate treasury delta if applied earlier
                try:
                    if delta != 0:
                        if delta > 0:
                            # reverse: sender → treasury
                            client.create_transfer_sync({
                                "amount": str(round_usdc(delta)),
                                "on_behalf_of": sender_wallet.customer_id,
                                "client_reference_id": f"{send_bundle_id}-comp",
                                "source": {"payment_rail": "bridge_wallet", "bridge_wallet_id": sender_wallet.wallet_id, "currency": "usdc"},
                                "destination": {"payment_rail": "solana", "bridge_wallet_id": TREASURY_WALLET_ID, "currency": "usdc"},
                            })
                        else:
                            # reverse: treasury → sender
                            client.create_transfer_sync({
                                "amount": str(round_usdc(abs(delta))),
                                "on_behalf_of": TREASURY_CUSTOMER_ID,
                                "client_reference_id": f"{send_bundle_id}-comp",
                                "source": {"payment_rail": "bridge_wallet", "bridge_wallet_id": TREASURY_WALLET_ID, "currency": "usdc"},
                                "destination": {"payment_rail": "solana", "bridge_wallet_id": sender_wallet.wallet_id, "currency": "usdc"},
                            })
                except Exception:
                    pass
                raise w2w_err

            # Immediately sync on-chain balances when Bridge returns (typically state='in_review')
            try:
                sw_now = client.get_wallet(sender_wallet.customer_id, sender_wallet.wallet_id)
                rw_now = client.get_wallet(recipient_wallet.customer_id, recipient_wallet.wallet_id)
                sender_wallet.balances = sw_now.get("balances", [])
                recipient_wallet.balances = rw_now.get("balances", [])
                sender_wallet.updated_at = datetime.utcnow()
                recipient_wallet.updated_at = datetime.utcnow()
                db.add(sender_wallet)
                db.add(recipient_wallet)
                db.commit()
            except Exception:
                pass


            # Refresh balances (best-effort)
            try:
                sw = client.get_wallet(sender_wallet.customer_id, sender_wallet.wallet_id)
                rw = client.get_wallet(recipient_wallet.customer_id, recipient_wallet.wallet_id)
                sender_wallet.balances = sw.get("balances", [])
                recipient_wallet.balances = rw.get("balances", [])
                sender_wallet.updated_at = datetime.utcnow()
                recipient_wallet.updated_at = datetime.utcnow()
                db.add(sender_wallet)
                db.add(recipient_wallet)
                # Reconcile fiat buckets: recipient gets fiat equal to usdc_live / recipient_rate, sender already reduced by send_amount
                # If recipient on-chain USDC is zero and we credited fiat, keep fiat (we credit at rate regardless of on-chain)
                # Ensure no negative or leftover artifacts
                try:
                    # Set recipient fiat to the precise credited amount (merge with existing)
                    credited = (round_usdc(usdc_live) / recipient_rate)
                    recipient_wallet.fiat_balance_by_rate = add_to_rate_bucket(
                        recipient_wallet.fiat_balance_by_rate or {}, recipient_rate, credited
                    )
                    # Sender fiat buckets already updated; nothing to add
                except Exception:
                    pass
                db.commit()
            except Exception:
                pass

            # Persist packaged send transaction
            consumed_serialized = [{"amount": float(a), "locked_rate": float(r)} for (a, r) in consumed]
            final_usdc = float(usdc_locked + delta)
            send_row = SendTransaction(
                send_id=send_bundle_id,
                sender_user_id=sender.id,
                recipient_user_id=recipient.id,
                sender_wallet_id=sender_wallet.wallet_id,
                recipient_wallet_id=recipient_wallet.wallet_id,
                sender_currency=sender_currency.lower(),
                recipient_currency=recipient_currency.lower(),
                sender_fiat_amount=float(send_amount),
                consumed_buckets=consumed_serialized,
                live_sender_rate_used=float(sender_rate),
                usdc_amount_sent=float(round_usdc(usdc_live)),
                delta_usdc=float(round_usdc(delta)),
                final_usdc_to_recipient=float(round_usdc(usdc_live)),
                live_recipient_rate_used=float(recipient_rate),
                recipient_fiat_amount=float(send_amount),
                exchange_rate=1.0,
                memo=body.memo or None,
                status="completed",
            )
            db.add(send_row)

            # Persist transfer receipts
            now = datetime.utcnow()
            # Row A: wallet_to_wallet
            db.add(Transfer(
                transfer_id=w2w.get("id", str(uuid.uuid4())),
                customer_id=sender_wallet.customer_id,
                user_id=sender.id,
                client_reference_id=str(send_bundle_id),
                amount=str(round_usdc(usdc_live)),
                currency="usdc",
                on_behalf_of=sender_wallet.customer_id,
                developer_fee="0",
                source={"payment_rail": "bridge_wallet", "bridge_wallet_id": sender_wallet.wallet_id},
                destination={"payment_rail": "solana", "bridge_wallet_id": recipient_wallet.wallet_id},
                state=w2w.get("state", "completed"),
                receipt={
                    "leg": "wallet_to_wallet",
                    "internal": False,
                    "currency_pair": f"{sender_currency.upper()}_{recipient_currency.upper()}",
                    "consumed_buckets": [{"amount": float(a), "locked_rate": float(r)} for (a, r) in consumed],
                    "live_sender_rate_used": float(sender_rate),
                    "usdc_amount_sent": float(round_usdc(usdc_live)),
                    "delta_usdc": float(round_usdc(delta)),
                    "final_usdc_to_recipient": float(round_usdc(usdc_live))
                },
                created_at=now,
                updated_at=now,
                return_details=None
            ))
            # Row B: treasury_settlement (internal)
            if delta != 0 and tsx is not None:
                db.add(Transfer(
                    transfer_id=tsx.get("id", str(uuid.uuid4())),
                    customer_id=(TREASURY_CUSTOMER_ID if delta > 0 else sender_wallet.customer_id),
                    user_id=sender.id,
                    client_reference_id=str(send_bundle_id),
                    amount=str(round_usdc(abs(delta))),
                    currency="usdc",
                    on_behalf_of=(TREASURY_CUSTOMER_ID if delta > 0 else sender_wallet.customer_id),
                    developer_fee="0",
                    source=(
                        {"payment_rail": "bridge_wallet", "bridge_wallet_id": TREASURY_WALLET_ID}
                        if delta > 0 else
                        {"payment_rail": "bridge_wallet", "bridge_wallet_id": sender_wallet.wallet_id}
                    ),
                    destination=(
                        {"payment_rail": "solana", "bridge_wallet_id": sender_wallet.wallet_id}
                        if delta > 0 else
                        {"payment_rail": "solana", "bridge_wallet_id": TREASURY_WALLET_ID}
                    ),
                    state=tsx.get("state", "completed"),
                    receipt={
                        "leg": "treasury_settlement",
                        "internal": True,
                        "currency_pair": f"{sender_currency.upper()}_{recipient_currency.upper()}",
                        "live_sender_rate_used": float(sender_rate),
                        "delta_usdc": float(round_usdc(delta))
                    },
                    created_at=now,
                    updated_at=now,
                    return_details=None
                ))

            db.commit()

            # Background refresh after 60 seconds
            def _refresh_later(w2w_id: str, tsx_id: Optional[str], s_customer_id: str, s_wallet_id: str, r_customer_id: str, r_wallet_id: str):
                import time
                from ..database import SessionLocal
                time.sleep(60)
                sess = SessionLocal()
                try:
                    client = BridgeClient()
                    def _update_one(tid: str):
                        data = client.get_transfer(tid)
                        tr = sess.query(Transfer).filter(Transfer.transfer_id == tid).first()
                        if tr:
                            tr.state = data.get("state", tr.state)
                            tr.updated_at = datetime.utcnow()
                            tr.receipt = data.get("receipt", tr.receipt)
                            sess.commit()
                    if w2w_id:
                        _update_one(w2w_id)
                    if tsx_id:
                        _update_one(tsx_id)

                    # Refresh wallet balances from Bridge after processing window (no fiat bucket changes)
                    try:
                        sw = client.get_wallet(s_customer_id, s_wallet_id)
                        rw = client.get_wallet(r_customer_id, r_wallet_id)
                        s_row = sess.query(BridgeWallet).filter(BridgeWallet.wallet_id == s_wallet_id).first()
                        r_row = sess.query(BridgeWallet).filter(BridgeWallet.wallet_id == r_wallet_id).first()
                        if s_row:
                            s_row.balances = sw.get("balances", [])
                        if r_row:
                            r_row.balances = rw.get("balances", [])
                        sess.commit()
                    except Exception:
                        pass
                except Exception:
                    try:
                        sess.rollback()
                    except Exception:
                        pass
                finally:
                    sess.close()

            if background_tasks is not None:
                background_tasks.add_task(_refresh_later, w2w.get("id"), tsx.get("id") if tsx else None, sender_wallet.customer_id, sender_wallet.wallet_id, recipient_wallet.customer_id, recipient_wallet.wallet_id)

            return SendOut(
                transfer_id=w2w.get("id", str(uuid.uuid4())),
                status="completed",
                sender_currency=sender_currency,
                recipient_currency=recipient_currency,
                amount_sent=float(send_amount),
                amount_received=float(send_amount),
                exchange_rate=1.0
            )
        else:
            # Cross-currency send (C1 → C2)
            # Convert sender amount to USDC using sender_rate; compute recipient fiat using recipient_rate
            usdc_live = round_usdc(send_amount * sender_rate)
            # Deduct from sender (highest-rate-first), computing USDC_locked
            updated, consumed, usdc_locked = deduct_highest_rates(
                sender_wallet.fiat_balance_by_rate or {}, send_amount
            )
            sender_wallet.fiat_balance_by_rate = updated

            # Treasury settlement before wallet-to-wallet: compute delta and adjust
            delta = round_usdc(usdc_live - round_usdc(usdc_locked))
            tsx = None
            if delta != 0:
                if delta > 0:
                    tsx = client.create_transfer_sync({
                        "amount": str(round_usdc(delta)),
                        "on_behalf_of": TREASURY_CUSTOMER_ID,
                        "client_reference_id": str(send_bundle_id),
                        "source": {
                            "payment_rail": "bridge_wallet",
                            "bridge_wallet_id": TREASURY_WALLET_ID,
                            "currency": "usdc"
                        },
                        "destination": {
                            "payment_rail": "solana",
                            "bridge_wallet_id": sender_wallet.wallet_id,
                            "currency": "usdc"
                        }
                    })
                else:
                    tsx = client.create_transfer_sync({
                        "amount": str(round_usdc(abs(delta))),
                        "on_behalf_of": sender_wallet.customer_id,
                        "client_reference_id": str(send_bundle_id),
                        "source": {
                            "payment_rail": "bridge_wallet",
                            "bridge_wallet_id": sender_wallet.wallet_id,
                            "currency": "usdc"
                        },
                        "destination": {
                            "payment_rail": "solana",
                            "bridge_wallet_id": TREASURY_WALLET_ID,
                            "currency": "usdc"
                        }
                    })

            try:
                w2w = client.create_transfer_sync({
                    "amount": str(round_usdc(usdc_live)),
                    "on_behalf_of": sender_wallet.customer_id,
                    "client_reference_id": str(send_bundle_id),
                    "source": {
                        "payment_rail": "bridge_wallet",
                        "bridge_wallet_id": sender_wallet.wallet_id,
                        "currency": "usdc"
                    },
                    "destination": {
                        "payment_rail": "solana",
                        "bridge_wallet_id": recipient_wallet.wallet_id,
                        "currency": "usdc"
                    }
                })
            except Exception as w2w_err:
                # Compensate treasury delta if applied earlier
                try:
                    if delta != 0:
                        if delta > 0:
                            # reverse: sender → treasury
                            client.create_transfer_sync({
                                "amount": str(round_usdc(delta)),
                                "on_behalf_of": sender_wallet.customer_id,
                                "client_reference_id": f"{send_bundle_id}-comp",
                                "source": {"payment_rail": "bridge_wallet", "bridge_wallet_id": sender_wallet.wallet_id, "currency": "usdc"},
                                "destination": {"payment_rail": "solana", "bridge_wallet_id": TREASURY_WALLET_ID, "currency": "usdc"},
                            })
                        else:
                            # reverse: treasury → sender
                            client.create_transfer_sync({
                                "amount": str(round_usdc(abs(delta))),
                                "on_behalf_of": TREASURY_CUSTOMER_ID,
                                "client_reference_id": f"{send_bundle_id}-comp",
                                "source": {"payment_rail": "bridge_wallet", "bridge_wallet_id": TREASURY_WALLET_ID, "currency": "usdc"},
                                "destination": {"payment_rail": "solana", "bridge_wallet_id": sender_wallet.wallet_id, "currency": "usdc"},
                            })
                except Exception:
                    pass
                raise w2w_err

            # Immediately sync on-chain balances when Bridge returns (typically state='in_review')
            try:
                sw_now = client.get_wallet(sender_wallet.customer_id, sender_wallet.wallet_id)
                rw_now = client.get_wallet(recipient_wallet.customer_id, recipient_wallet.wallet_id)
                sender_wallet.balances = sw_now.get("balances", [])
                recipient_wallet.balances = rw_now.get("balances", [])
                sender_wallet.updated_at = datetime.utcnow()
                recipient_wallet.updated_at = datetime.utcnow()
                db.add(sender_wallet)
                db.add(recipient_wallet)
                db.commit()
            except Exception:
                pass


            # Recipient receives exactly usdc_live
            recipient_amount = (round_usdc(usdc_live) / recipient_rate)
            # Round recipient fiat to 2 decimals for persistence/display
            recipient_amount = round_fiat(recipient_amount)
            recipient_wallet.fiat_balance_by_rate = add_to_rate_bucket(
                recipient_wallet.fiat_balance_by_rate or {}, recipient_rate, recipient_amount
            )

            # Refresh balances (best-effort)
            try:
                sw = client.get_wallet(sender_wallet.customer_id, sender_wallet.wallet_id)
                rw = client.get_wallet(recipient_wallet.customer_id, recipient_wallet.wallet_id)
                sender_wallet.balances = sw.get("balances", [])
                recipient_wallet.balances = rw.get("balances", [])
                sender_wallet.updated_at = datetime.utcnow()
                recipient_wallet.updated_at = datetime.utcnow()
                db.add(sender_wallet)
                db.add(recipient_wallet)
                db.commit()
            except Exception:
                pass

            # Persist packaged send transaction
            consumed_serialized = [{"amount": float(a), "locked_rate": float(r)} for (a, r) in consumed]
            # Quantize exchange rate to 6 dp for display
            _ex_rate = (recipient_amount / send_amount).quantize(Decimal("0.000001"))
            send_row = SendTransaction(
                send_id=send_bundle_id,
                sender_user_id=sender.id,
                recipient_user_id=recipient.id,
                sender_wallet_id=sender_wallet.wallet_id,
                recipient_wallet_id=recipient_wallet.wallet_id,
                sender_currency=sender_currency.lower(),
                recipient_currency=recipient_currency.lower(),
                sender_fiat_amount=float(send_amount),
                consumed_buckets=consumed_serialized,
                live_sender_rate_used=float(sender_rate),
                usdc_amount_sent=float(round_usdc(usdc_live)),
                delta_usdc=float(round_usdc(delta)),
                final_usdc_to_recipient=float(round_usdc(usdc_live)),
                live_recipient_rate_used=float(recipient_rate),
                recipient_fiat_amount=float(recipient_amount),
                exchange_rate=float(_ex_rate),
                memo=body.memo or None,
                status="completed",
            )
            db.add(send_row)

            # Persist transfer receipts
            now = datetime.utcnow()
            # Row A: wallet_to_wallet
            db.add(Transfer(
                transfer_id=w2w.get("id", str(uuid.uuid4())),
                customer_id=sender_wallet.customer_id,
                user_id=sender.id,
                client_reference_id=str(send_bundle_id),
                amount=str(round_usdc(usdc_live)),
                currency="usdc",
                on_behalf_of=sender_wallet.customer_id,
                developer_fee="0",
                source={"payment_rail": "bridge_wallet", "bridge_wallet_id": sender_wallet.wallet_id},
                destination={"payment_rail": "solana", "bridge_wallet_id": recipient_wallet.wallet_id},
                state=w2w.get("state", "completed"),
                receipt={
                    "leg": "wallet_to_wallet",
                    "internal": False,
                    "currency_pair": f"{sender_currency.upper()}_{recipient_currency.upper()}",
                    "consumed_buckets": [{"amount": float(a), "locked_rate": float(r)} for (a, r) in consumed],
                    "live_sender_rate_used": float(sender_rate),
                    "usdc_amount_sent": float(round_usdc(usdc_live)),
                    "delta_usdc": float(round_usdc(delta)),
                    "final_usdc_to_recipient": float(round_usdc(usdc_live))
                },
                created_at=now,
                updated_at=now,
                return_details=None
            ))
            # Row B: treasury_settlement (internal)
            if delta != 0 and tsx is not None:
                db.add(Transfer(
                    transfer_id=tsx.get("id", str(uuid.uuid4())),
                    customer_id=(TREASURY_CUSTOMER_ID if delta > 0 else sender_wallet.customer_id),
                    user_id=sender.id,
                    client_reference_id=str(send_bundle_id),
                    amount=str(round_usdc(abs(delta))),
                    currency="usdc",
                    on_behalf_of=(TREASURY_CUSTOMER_ID if delta > 0 else sender_wallet.customer_id),
                    developer_fee="0",
                    source=(
                        {"payment_rail": "bridge_wallet", "bridge_wallet_id": TREASURY_WALLET_ID}
                        if delta > 0 else
                        {"payment_rail": "bridge_wallet", "bridge_wallet_id": sender_wallet.wallet_id}
                    ),
                    destination=(
                        {"payment_rail": "solana", "bridge_wallet_id": sender_wallet.wallet_id}
                        if delta > 0 else
                        {"payment_rail": "solana", "bridge_wallet_id": TREASURY_WALLET_ID}
                    ),
                    state=tsx.get("state", "completed"),
                    receipt={
                        "leg": "treasury_settlement",
                        "internal": True,
                        "currency_pair": f"{sender_currency.upper()}_{recipient_currency.upper()}",
                        "live_sender_rate_used": float(sender_rate),
                        "delta_usdc": float(round_usdc(delta))
                },
                created_at=now,
                updated_at=now,
                return_details=None
            ))

            db.commit()

            # Background refresh after 60 seconds
            def _refresh_later(w2w_id: str, tsx_id: Optional[str], s_customer_id: str, s_wallet_id: str, r_customer_id: str, r_wallet_id: str):
                import time
                from ..database import SessionLocal
                time.sleep(60)
                sess = SessionLocal()
                try:
                    client = BridgeClient()
                    def _update_one(tid: str):
                        data = client.get_transfer(tid)
                        tr = sess.query(Transfer).filter(Transfer.transfer_id == tid).first()
                        if tr:
                            tr.state = data.get("state", tr.state)
                            tr.updated_at = datetime.utcnow()
                            tr.receipt = data.get("receipt", tr.receipt)
                            sess.commit()
                    if w2w_id:
                        _update_one(w2w_id)
                    if tsx_id:
                        _update_one(tsx_id)

                    # Refresh wallet balances from Bridge after processing window (no fiat bucket changes)
                    try:
                        sw = client.get_wallet(s_customer_id, s_wallet_id)
                        rw = client.get_wallet(r_customer_id, r_wallet_id)
                        s_row = sess.query(BridgeWallet).filter(BridgeWallet.wallet_id == s_wallet_id).first()
                        r_row = sess.query(BridgeWallet).filter(BridgeWallet.wallet_id == r_wallet_id).first()
                        if s_row:
                            s_row.balances = sw.get("balances", [])
                        if r_row:
                            r_row.balances = rw.get("balances", [])
                        sess.commit()
                    except Exception:
                        pass
                except Exception:
                    try:
                        sess.rollback()
                    except Exception:
                        pass
                finally:
                    sess.close()

            if background_tasks is not None:
                background_tasks.add_task(_refresh_later, w2w.get("id"), tsx.get("id") if tsx else None, sender_wallet.customer_id, sender_wallet.wallet_id, recipient_wallet.customer_id, recipient_wallet.wallet_id)

            return SendOut(
                transfer_id=w2w.get("id", str(uuid.uuid4())),
                status="completed",
                sender_currency=sender_currency,
                recipient_currency=recipient_currency,
                amount_sent=float(send_amount),
                amount_received=float(recipient_amount),
                exchange_rate=float(_ex_rate)
            )
            
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Transfer failed: {str(e)}")

@router.post("/deposit", response_model=DepositOut)
async def deposit_fiat_to_wallet(
    body: DepositIn,
    db: Session = Depends(get_db),
    auth_user: Auth0User = Depends(get_current_user),
):
    """Start a fiat deposit (bank push) and immediately credit the user's on-chain wallet with USDB.

    Steps:
    1. Create bridge transfer: external_account_id ➜ corporate account treasury wallet (fiat rails).
    2. Advance USDB from treasury wallet ➜ user's bridge wallet.
    3. Persist encumbrance so funds can be clawed back if fiat leg fails.
    """

    user = _get_user_by_sub(db, auth_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get bridge customer and wallet from related tables
    bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == user.id).first()
    if not bridge_customer:
        raise HTTPException(status_code=400, detail="Bridge customer not found")
    
    bridge_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == user.id).first()
    if not bridge_wallet:
        raise HTTPException(status_code=400, detail="Bridge wallet not found")

    if not TREASURY_WALLET_ID or not TREASURY_CUSTOMER_ID:
        raise HTTPException(status_code=500, detail="Treasury configuration missing on server")

    client = BridgeClient()
    # Fetch the external account to determine currency and appropriate on-ramp rail
    try:
        ext_acct = client.get_external_account(body.external_account_id, bridge_customer.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid external account: {e}")

    # ------------------------------------------------------------------
    # Plaid balance guardrail – ensure sufficient funds before pushing ACH
    # ------------------------------------------------------------------

    from ..services.plaid_client import PlaidClient  # local import to avoid cycles

    plaid_item = db.query(PlaidItem).filter(PlaidItem.external_account_id == body.external_account_id).first()
    if plaid_item:
        try:
            bal_resp = PlaidClient(force_production=True).get_balance(plaid_item.access_token)
            # Sum available balance across matching accounts
            available_sum = 0
            for acct in bal_resp.get("accounts", []):
                avail = acct.get("balances", {}).get("available")
                if avail is not None:
                    available_sum += float(avail)

            if available_sum < float(body.amount):
                raise HTTPException(status_code=400, detail="Insufficient bank balance to cover deposit amount")
        except HTTPException:
            raise
        except Exception as e:
            # Non-fatal – log warning but continue; Bridge will still attempt ACH
            import logging
            logging.getLogger(__name__).warning("Plaid balance check failed: %s", e)

    currency = (ext_acct.get("currency") or "usd").lower()
    rail_by_cur = {"usd": "ach_push", "eur": "sepa"}
    if currency not in rail_by_cur:
        raise HTTPException(status_code=400, detail=f"Unsupported external account currency: {currency}")

    payment_rail = rail_by_cur[currency]

    # ------------------------------------------------------------------
    # Generate Plaid processor token & initiate ACH debit via Seamless Chex
    # ------------------------------------------------------------------
    processor_token = None
    if plaid_item:
        from ..services.seamless_chex_client import SeamlessChexClient, SeamlessChexError  # local import
        try:
            auth_resp = PlaidClient(force_production=True).get_auth(plaid_item.access_token)
            # Pick first account (or first checking/savings) for processor token
            accounts = auth_resp.get("accounts", [])
            if not accounts:
                raise ValueError("No accounts returned by Plaid Auth")
            preferred = next((a for a in accounts if a.get("subtype") in ("checking", "savings")), accounts[0])
            account_id_for_token = preferred["account_id"]

            proc_resp = PlaidClient(force_production=True).create_processor_token(
                plaid_item.access_token,
                account_id=account_id_for_token,
                processor="seamless_chex",
            )
            processor_token = proc_resp.get("processor_token")
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning("Failed to create processor token for Seamless Chex: %s", e)

    # Initiate debit via Seamless Chex if we have a processor token
    if processor_token:
        try:
            dest_acct_id = os.getenv("SEAMLESSCHEX_DESTINATION_ACCOUNT_ID")
            chex = SeamlessChexClient()
            chex_resp = chex.initiate_debit(
                processor_token=processor_token,
                amount=Decimal(str(body.amount)),
                currency=currency.upper(),
                description="Liquicity fiat deposit",
                destination_account_id=dest_acct_id,
            )
            # Optionally persist chex_resp somewhere or include in response
        except Exception as e:
            import logging
            logging.getLogger(__name__).error("Seamless Chex debit failed: %s", e)
            # Non-fatal for now – continue with Bridge on-ramp so deposit isn't blocked

    # Fetch current exchange rate currency -> USDB so we can credit user immediately
    try:
        if currency == "usd":
            # USDB is 1:1 pegged to USD – no conversion needed
            usdb_amount_dec = Decimal(str(body.amount))
        else:
            # Bridge only provides USD→EUR and USD→MXN rates. Invert to get EUR/MXN → USD.
            rate_data = client.get_exchange_rate("usd", currency)
            rate_usd_to_cur = Decimal(str(rate_data.get("rate") or rate_data.get("exchange_rate") or 0))
            if rate_usd_to_cur == 0:
                raise ValueError("Rate missing in response")
            # amount (currency) × (USD / currency) = USD equivalent
            usdb_amount_dec = (Decimal(str(body.amount)) / rate_usd_to_cur).quantize(Decimal("0.000001"))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch exchange rate: {e}")

    # ---------------- Treasury liquidity check ----------------
    try:
        treas_wallet = client.get_wallet(TREASURY_CUSTOMER_ID, TREASURY_WALLET_ID)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Treasury wallet not found or unreachable: {e}")

    bal_list = treas_wallet.get("balances", [])
    treas_usdb = Decimal("0")
    for b in bal_list:
        if b.get("currency", "").lower() == "usdb":
            treas_usdb = Decimal(str(b.get("available_balance") or b.get("balance") or 0))
            break

    if treas_usdb < usdb_amount_dec:
        raise HTTPException(status_code=400, detail="Treasury liquidity insufficient to cover instant credit. Please try again later.")

    fiat_payload: Dict[str, Any] = {
        "amount": str(body.amount),
        "on_behalf_of": bridge_customer.id,
        "source": {
            "payment_rail": payment_rail,
            "currency": currency,
            "external_account_id": body.external_account_id,
        },
        "destination": {
            "payment_rail": "solana",
            "currency": "usdb",
            "bridge_wallet_id": TREASURY_WALLET_ID,
        },
        "convert_to_currency": "usdb",
    }
    try:
        fiat_tx = client.create_transfer_sync(fiat_payload)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to initiate fiat transfer: {e}")

    # Guardrail: proceed with instant credit only if Bridge immediately returned state=='pending'
    fiat_state = fiat_tx.get("state")
    if fiat_state != "pending":
        # Do not advance funds; let normal settlement complete first
        return DepositOut(
            fiat_transfer_id=fiat_tx["id"],
            advance_transfer_id="",
            encumbrance_id="",
            state=fiat_state,
        )

    # 2. Advance USDB to user using the rate-based amount
    usdb_amount = str(usdb_amount_dec)
    advance_payload: Dict[str, Any] = {
        "amount": usdb_amount,
        "on_behalf_of": TREASURY_CUSTOMER_ID,  # treasury sends on its own behalf
        "source": {
            "payment_rail": "solana",
            "currency": "usdb",
            "bridge_wallet_id": TREASURY_WALLET_ID,
        },
        "destination": {
            "payment_rail": "solana",
            "currency": "usdb",
            "bridge_wallet_id": bridge_wallet.wallet_id,
        },
    }

    try:
        advance_tx = client.create_transfer_sync(advance_payload)
    except Exception as e:
        # Cancel the fiat on-ramp since treasury couldn't advance funds
        try:
            client.delete_transfer(fiat_tx["id"])
        except Exception as cancel_err:
            # Log but surface original error
            import logging
            logging.getLogger(__name__).error("Failed to cancel fiat transfer %s after advance failure: %s", fiat_tx["id"], cancel_err)

        raise HTTPException(status_code=502, detail=f"Advance payout failed; deposit cancelled: {e}")

    # 3. Record encumbrance
    svc = EncumbranceService(db)
    enc = svc.create_encumbrance(
        fiat_transfer_id=fiat_tx["id"],
        user_wallet_id=bridge_wallet.wallet_id,
        amount=usdb_amount_dec,
    )

    return DepositOut(
        fiat_transfer_id=fiat_tx["id"],
        advance_transfer_id=advance_tx["id"],
        encumbrance_id=str(enc.id),
        state=fiat_tx.get("state", "pending"),
    )


@router.post("/deposits", response_model=DepositOut, include_in_schema=False)
async def deposit_alias_transfers(
    body: DepositIn,
    db: Session = Depends(get_db),
    auth_user: Auth0User = Depends(get_current_user),
):
    """Alias for legacy frontend which calls /deposits under /transfers/deposits."""
    return await deposit_fiat_to_wallet(body, db, auth_user)


# Root-level alias
# This route has no /transfers prefix because it belongs to `public_router`.
@public_router.post("/deposits", response_model=DepositOut)
async def deposit_alias_root(
    body: DepositIn,
    db: Session = Depends(get_db),
    auth_user: Auth0User = Depends(get_current_user),
):
    """Root-level /deposits alias for frontend convenience."""
    return await deposit_fiat_to_wallet(body, db, auth_user)


@router.post("/withdraw_preview", response_model=WithdrawalPreviewOut)
async def withdraw_preview(
    body: WithdrawalIn,
    db: Session = Depends(get_db),
    auth_user: Auth0User = Depends(get_current_user),
):
    """Preview expected receive amount for a withdrawal (estimate, not a quote)."""
    user = _get_user_by_sub(db, auth_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == user.id).first()
    if not bridge_customer:
        raise HTTPException(status_code=400, detail="Bridge customer not found")

    bridge_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == user.id).first()
    if not bridge_wallet:
        raise HTTPException(status_code=400, detail="Bridge wallet not found")

    client = BridgeClient()
    try:
        ext_acct = client.get_external_account(body.external_account_id, bridge_customer.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid external account: {e}")

    dest_cur = (ext_acct.get("currency") or "usd").lower()
    main_cur = (bridge_wallet.fiat_currency or "USD").lower()

    dev_fee_pct = Decimal("0.015")
    withdraw_amt_dest = Decimal(str(body.amount))  # User enters amount in DESTINATION currency

    if main_cur == dest_cur:
        # Same currency: user enters $100, receives $98.50 after fee
        expected = withdraw_amt_dest * (Decimal("1") - dev_fee_pct)
        return WithdrawalPreviewOut(
            from_currency=main_cur.upper(),
            to_currency=dest_cur.upper(),
            withdraw_amount=float(withdraw_amt_dest),
            developer_fee_percent=float(dev_fee_pct * 100),
            expected_receive_amount=float(round_fiat(expected)),
            buy_rate_used=None,
        )
    
    # Cross currency: user enters €100, we show how much USD deducted and €100 received
    # Get main → dest FX rate to compute deduction from main currency buckets
    try:
        fx_rate = rate_service.get_exchange_rate(main_cur.upper(), dest_cur.upper())
        if fx_rate is None or fx_rate == 0:
            raise ValueError("Invalid FX rate")
        # withdraw_amt_main = withdraw_amt_dest / fx_rate (e.g., €100 / 0.92 = $108.70)
        withdraw_amt_main = round_fiat(withdraw_amt_dest / fx_rate)
    except Exception:
        raise HTTPException(status_code=502, detail=f"Failed to fetch {main_cur.upper()}/{dest_cur.upper()} FX rate for preview")

    # User receives withdraw_amt_dest after Bridge's fee (already included in our calculation)
    # Show: "Withdraw €100 from your USD balance (~$108.70 will be deducted after fees)"
    return WithdrawalPreviewOut(
        from_currency=main_cur.upper(),
        to_currency=dest_cur.upper(),
        withdraw_amount=float(withdraw_amt_main),  # Amount deducted from main currency
        developer_fee_percent=float(dev_fee_pct * 100),
        expected_receive_amount=float(withdraw_amt_dest),  # Amount user will receive in dest currency
        buy_rate_used=float(fx_rate),  # FX rate used
    )


@router.post("/withdraw", response_model=Dict[str, Any])
async def withdraw_fiat_from_wallet(
    body: WithdrawalIn,
    db: Session = Depends(get_db),
    auth_user: Auth0User = Depends(get_current_user),
    request: Request = None,
):
    """Initiate a fiat withdrawal: Bridge wallet ➜ external bank account, with dev fee and variance handling."""
    user = _get_user_by_sub(db, auth_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get bridge customer and wallet from related tables (lock wallet)
    bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == user.id).first()
    if not bridge_customer:
        raise HTTPException(status_code=400, detail="Bridge customer not found")
    
    bridge_wallet = (
        db.query(BridgeWallet)
        .with_for_update()
        .filter(BridgeWallet.user_id == user.id)
        .first()
    )
    if not bridge_wallet:
        raise HTTPException(status_code=400, detail="Bridge wallet not found")

    client = BridgeClient()

    # Fetch external account to validate ownership & get currency
    try:
        ext_acct = client.get_external_account(body.external_account_id, bridge_customer.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid external account: {e}")

    currency = (ext_acct.get("currency") or "usd").lower()
    # Bridge rails per docs: USD→ACH push, EUR→SEPA credit transfer
    rail_by_cur = {"usd": "ach_push", "eur": "sepa_credit_transfer"}
    if currency not in rail_by_cur:
        raise HTTPException(status_code=400, detail=f"Unsupported withdrawal currency: {currency}")

    payment_rail = rail_by_cur[currency]
    # Compute treasury variance using locked buckets vs live rate in main currency
    main_cur = (bridge_wallet.fiat_currency or "USD").lower()
    dest_cur = currency.lower()
    
    # Amount is in DESTINATION currency; convert to main currency if needed
    withdraw_amt_dest = Decimal(str(body.amount))  # Amount in destination currency (e.g., €100)
    
    # Convert destination amount to main currency amount
    if main_cur == dest_cur:
        # Same currency: no conversion needed
        withdraw_amt_main = withdraw_amt_dest
        fx_rate_main_to_dest = Decimal("1.0")
    else:
        # Cross-currency: convert dest → main using Bridge FX
        fx_rate_main_to_dest = rate_service.get_exchange_rate(main_cur.upper(), dest_cur.upper())
        if fx_rate_main_to_dest is None or fx_rate_main_to_dest == 0:
            raise HTTPException(status_code=502, detail=f"Failed to fetch {main_cur.upper()}/{dest_cur.upper()} exchange rate")
        # withdraw_amt_main = withdraw_amt_dest / fx_rate (e.g., €100 / 0.92 = $108.70)
        withdraw_amt_main = round_fiat(withdraw_amt_dest / fx_rate_main_to_dest)
    
    # Deduct from main currency buckets
    try:
        updated_buckets, consumed, usdc_locked = deduct_highest_rates(bridge_wallet.fiat_balance_by_rate or {}, withdraw_amt_main)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Live rate: USDC per 1 unit of main currency
    live_rate = rate_service.get_usdc_rate(main_cur.upper())
    if live_rate is None:
        raise HTTPException(status_code=502, detail="Failed to fetch current exchange rates")

    # Treasury variance in M: withdraw_M × (1 − live_r / stored_r). Here usdc_locked = withdraw_M × stored_r ⇒ stored_r = usdc_locked/withdraw_M
    stored_r = (round_usdc(usdc_locked) / withdraw_amt_main) if withdraw_amt_main != 0 else Decimal("0")
    variance_M = Decimal("0")
    try:
        variance_M = withdraw_amt_main * (Decimal("1") - (live_rate / stored_r)) if stored_r != 0 else Decimal("0")
    except Exception:
        variance_M = Decimal("0")

    # Apply policy
    apply_profit = bool(body.apply_profit_to_user)
    effective_debit = withdraw_amt_main + (variance_M if apply_profit else max(Decimal("0"), variance_M))

    # Stage wallet bucket deduction in the current transaction (no commit yet).
    # We will commit only after Bridge accepts the transfer; otherwise we'll roll back.
    bridge_wallet.fiat_balance_by_rate = updated_buckets
    db.add(bridge_wallet)

    # Execute treasury variance settlement BEFORE withdrawal
    # usdc_live = withdraw_amt_main × live_rate (what we actually withdraw in USDC)
    # usdc_locked = what was locked in buckets at stored rates
    # delta = usdc_live - usdc_locked
    #   > 0: treasury owes user (treasury → user)
    #   < 0: user owes treasury (user → treasury, profit)
    usdc_live = round_usdc(withdraw_amt_main * live_rate)
    delta_usdc = round_usdc(usdc_live - round_usdc(usdc_locked))
    
    tsx = None
    if delta_usdc != 0:
        try:
            if delta_usdc > 0:
                # Compensation: treasury → user
                tsx = client.create_transfer_sync({
                    "amount": str(round_usdc(delta_usdc)),
                    "on_behalf_of": TREASURY_CUSTOMER_ID,
                    "client_reference_id": f"wdl-var-{uuid.uuid4()}",
                    "source": {
                        "payment_rail": "bridge_wallet",
                        "bridge_wallet_id": TREASURY_WALLET_ID,
                        "currency": "usdc"
                    },
                    "destination": {
                        "payment_rail": "solana",
                        "bridge_wallet_id": bridge_wallet.wallet_id,
                        "currency": "usdc"
                    }
                })
            else:
                # Profit: user → treasury
                tsx = client.create_transfer_sync({
                    "amount": str(round_usdc(abs(delta_usdc))),
                    "on_behalf_of": bridge_customer.id,
                    "client_reference_id": f"wdl-var-{uuid.uuid4()}",
                    "source": {
                        "payment_rail": "bridge_wallet",
                        "bridge_wallet_id": bridge_wallet.wallet_id,
                        "currency": "usdc"
                    },
                    "destination": {
                        "payment_rail": "solana",
                        "bridge_wallet_id": TREASURY_WALLET_ID,
                        "currency": "usdc"
                    }
                })
        except Exception as var_err:
            # Log variance settlement failure but don't block withdrawal
            import logging
            logging.getLogger(__name__).error(f"Treasury variance settlement failed: {var_err}")

    # Build Bridge payload; developer fee 1.5%
    idem_key = None
    try:
        idem_key = request.headers.get("X-Idempotency-Key") if request else None
    except Exception:
        idem_key = None

    # Compute developer fee as 1.5% of destination amount and cap to be < amount
    dev_fee_dec = round_fiat(withdraw_amt_dest * Decimal("0.015"))
    if dev_fee_dec >= withdraw_amt_dest:
        # Ensure at least 0.01 less than amount if rounding pushes it over
        try:
            from decimal import ROUND_DOWN
            dev_fee_dec = (withdraw_amt_dest - Decimal("0.01")).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
            if dev_fee_dec < Decimal("0.00"):
                dev_fee_dec = Decimal("0.00")
        except Exception:
            dev_fee_dec = Decimal("0.00")

    # Enforce Bridge minimum: net payout after developer fee must be >= 1.00 in destination currency
    net_dest = withdraw_amt_dest - dev_fee_dec
    if net_dest < Decimal("1.00"):
        raise HTTPException(status_code=400, detail=f"Minimum payout after fee is 1.00 {dest_cur.upper()}. Increase amount.")

    payload = {
        "amount": str(withdraw_amt_dest),  # Amount in destination currency (what user wants to receive)
        "on_behalf_of": bridge_customer.id,
        # Per Bridge docs: send developer_fee as absolute amount in destination currency
        "developer_fee": str(dev_fee_dec),
        "source": {
            "payment_rail": "bridge_wallet",
            "currency": "usdc",
            "bridge_wallet_id": bridge_wallet.wallet_id,
        },
        "destination": {
            "payment_rail": payment_rail,
            "currency": currency,
            "external_account_id": body.external_account_id,
        },
        "client_reference_id": str(uuid.uuid4()),
    }

    try:
        transfer = client.create_transfer_sync(payload, idempotency_key=idem_key)
    except Exception as e:
        # Reverse variance settlement if it was executed
        try:
            if delta_usdc != 0 and tsx is not None:
                if delta_usdc > 0:
                    # previously treasury → user; reverse user → treasury
                    client.create_transfer_sync({
                        "amount": str(round_usdc(delta_usdc)),
                        "on_behalf_of": bridge_customer.id,
                        "client_reference_id": f"wdl-var-rev-{uuid.uuid4()}",
                        "source": {"payment_rail": "bridge_wallet", "bridge_wallet_id": bridge_wallet.wallet_id, "currency": "usdc"},
                        "destination": {"payment_rail": "solana", "bridge_wallet_id": TREASURY_WALLET_ID, "currency": "usdc"},
                    })
                else:
                    # previously user → treasury; reverse treasury → user
                    client.create_transfer_sync({
                        "amount": str(round_usdc(abs(delta_usdc))),
                        "on_behalf_of": TREASURY_CUSTOMER_ID,
                        "client_reference_id": f"wdl-var-rev-{uuid.uuid4()}",
                        "source": {"payment_rail": "bridge_wallet", "bridge_wallet_id": TREASURY_WALLET_ID, "currency": "usdc"},
                        "destination": {"payment_rail": "solana", "bridge_wallet_id": bridge_wallet.wallet_id, "currency": "usdc"},
                    })
        except Exception:
            pass
        # Roll back staged bucket deduction so balance isn't reduced on error
        try:
            db.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=502, detail=f"Bridge withdrawal failed: {e}")

    # Persist withdrawal transfer record for status tracking
    now = datetime.utcnow()
    db.add(Transfer(
        transfer_id=transfer.get("id", str(uuid.uuid4())),
        customer_id=bridge_customer.id,
        user_id=user.id,
        client_reference_id=payload.get("client_reference_id"),
        amount=str(withdraw_amt_dest),  # Amount in destination currency
        currency="usdc",
        on_behalf_of=bridge_customer.id,
        developer_fee=str(dev_fee_dec),
        source=payload["source"],
        destination=payload["destination"],
        state=transfer.get("state", "pending"),
        receipt={
            "type": "withdrawal",
            "main_currency": main_cur.upper(),
            "dest_currency": dest_cur.upper(),
            "withdraw_amt_dest": float(withdraw_amt_dest),  # What user receives
            "withdraw_amt_main": float(withdraw_amt_main),  # What was deducted from buckets
            "fx_rate_main_to_dest": float(fx_rate_main_to_dest),  # Conversion rate used
            "usdc_live": float(usdc_live),
            "usdc_locked": float(usdc_locked),
            "delta_usdc": float(delta_usdc),
            "variance_settlement_id": tsx.get("id") if tsx else None,
            "consumed_buckets": [{"amount": float(a), "locked_rate": float(r)} for (a, r) in consumed],
        },
        created_at=now,
        updated_at=now,
        return_details=None,
    ))
    db.commit()

    return transfer


@router.get("/withdraw/{transfer_id}/status")
async def get_withdrawal_status(
    transfer_id: str,
    db: Session = Depends(get_db),
    auth_user: Auth0User = Depends(get_current_user),
):
    """Poll withdrawal status from Bridge and return current state.
    
    States:
    - awaiting_funds: waiting for funds
    - pending: processing started
    - payment_submitted: sent to bank
    - payment_processed: SUCCESS ✅
    - failed: FAILED ❌
    """
    user = _get_user_by_sub(db, auth_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if transfer belongs to user (via Transfer table or direct Bridge call)
    transfer_record = db.query(Transfer).filter(
        Transfer.transfer_id == transfer_id,
        Transfer.user_id == user.id
    ).first()
    
    if not transfer_record:
        raise HTTPException(status_code=404, detail="Transfer not found or unauthorized")
    
    # Fetch live status from Bridge
    client = BridgeClient()
    try:
        live_data = client.get_transfer(transfer_id)
        
        # Update our DB record
        transfer_record.state = live_data.get("state", transfer_record.state)
        transfer_record.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "transfer_id": transfer_id,
            "state": live_data.get("state"),
            "amount": live_data.get("amount"),
            "currency": live_data.get("destination", {}).get("currency"),
            "created_at": live_data.get("created_at"),
            "updated_at": live_data.get("updated_at"),
            "is_complete": live_data.get("state") in ["payment_processed"],
            "is_failed": live_data.get("state") in ["failed", "canceled"],
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch transfer status: {e}")

# ---------------------------- Routes: Listing ----------------------------

@router.get("/transfers")
async def list_transfers(client_reference_id: Optional[str] = None, db: Session = Depends(get_db), auth_user: Auth0User = Depends(get_current_user)):
    """List transfer rows for the current user. Optionally filter by client_reference_id (send id)."""
    user = db.query(User).filter(User.auth0_id == auth_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    q = db.query(Transfer).filter(Transfer.user_id == user.id)
    if client_reference_id:
        q = q.filter(Transfer.client_reference_id == client_reference_id)
    rows = q.order_by(Transfer.created_at.desc()).limit(100).all()
    return {
        "transfers": [
            {
                "id": t.transfer_id,
                "client_reference_id": t.client_reference_id,
                "amount": t.amount,
                "currency": t.currency,
                "state": t.state,
                "on_behalf_of": t.on_behalf_of,
                "source": t.source,
                "destination": t.destination,
                "receipt": t.receipt,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None,
            }
            for t in rows
        ]
    } 

@router.post("/quote", response_model=QuoteOut)
async def quote_transfer(
    body: SendIn,
    db: Session = Depends(get_db),
    auth_user: Auth0User = Depends(get_current_user),
):
    """
    Computes the recipient's expected amount and exchange rate for a transfer
    without actually creating the transfer.
    """
    sender = _get_user_by_sub(db, auth_user.id)
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")
    
    recipient = _get_user_by_id(db, body.recipient_user_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    sender_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == sender.id).first()
    if not sender_wallet:
        raise HTTPException(status_code=400, detail="Sender wallet not found")
    
    recipient_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == recipient.id).first()
    if not recipient_wallet:
        raise HTTPException(status_code=400, detail="Recipient wallet not found")
    
    sender_currency = sender_wallet.fiat_currency or 'USD'
    recipient_currency = recipient_wallet.fiat_currency or 'USD'
    send_amount = body.amount
    
    # Get current rates for locking
    sender_rate = rate_service.get_usdc_rate(sender_currency)
    recipient_rate = rate_service.get_usdc_rate(recipient_currency)
    
    if sender_rate is None or recipient_rate is None:
        raise HTTPException(status_code=502, detail="Unable to fetch current exchange rates")
    
    # Compute recipient amount and exchange rate
    usdc_amount = send_amount * sender_rate
    recipient_amount = usdc_amount / recipient_rate
    
    # Round recipient amount to 2 decimal places for display
    recipient_amount = round_fiat(recipient_amount)
    
    return QuoteOut(
        sender_currency=sender_currency,
        recipient_currency=recipient_currency,
        amount_sent=float(send_amount),
        usdc_amount=float(usdc_amount),
        amount_received=float(recipient_amount),
        exchange_rate=float(sender_rate / recipient_rate)
    ) 