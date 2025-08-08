from decimal import Decimal
import os
from typing import Any, Dict, Optional
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, condecimal
from sqlalchemy.orm import Session

from ..auth import get_current_user
from fastapi_auth0.auth import Auth0User
from ..database import get_db
from ..models import User, BridgeCustomer, BridgeWallet
from ..bridge import BridgeClient
from ..services.encumbrance_service import EncumbranceService, CORPORATE_WALLET_ID, CORPORATE_CUSTOMER_ID
from ..services.rate_service import rate_service
from ..models import PlaidItem

router = APIRouter(prefix="/transfers", tags=["transfers"])

# Separate router with no prefix to expose legacy /deposits endpoint at root
public_router = APIRouter(tags=["transfers"], include_in_schema=False)


# ---------------------------- Schemas ----------------------------
class DepositIn(BaseModel):
    amount: condecimal(gt=Decimal("0"), max_digits=18, decimal_places=2)
    external_account_id: str

class SendIn(BaseModel):
    recipient_user_id: int
    amount: condecimal(gt=Decimal("0"), max_digits=18, decimal_places=2)
    memo: Optional[str] = None
    speed_option: Optional[str] = "standard"

class DepositOut(BaseModel):
    fiat_transfer_id: str
    usdb_transfer_id: str
    encumbrance_id: str
    status: str

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


# ---------------------------- Helpers ----------------------------

def _get_user_by_sub(db: Session, sub: str) -> Optional[User]:
    """Look up user by Auth0 subject ID only - NEVER by email to prevent auth bugs"""
    return db.query(User).filter(User.auth0_id == sub).first()

def _get_user_by_id(db: Session, user_id: int) -> Optional[User]:
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
    
    # Get sender's bridge wallet
    sender_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == sender.id).first()
    if not sender_wallet:
        raise HTTPException(status_code=400, detail="Sender wallet not found")
    
    # Get recipient's bridge wallet
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
    
    # Create rate keys for bucket tracking
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    sender_rate_key = f"R_{timestamp}_{sender_rate}"
    recipient_rate_key = f"R_{timestamp}_{recipient_rate}"
    
    try:
        if sender_currency.upper() == recipient_currency.upper():
            # Case 5: Same-currency send (H → H)
            
            # Deduct from sender's buckets
            sender_wallet.fiat_balance_by_rate = _deduct_from_buckets(
                sender_wallet.fiat_balance_by_rate or {}, send_amount
            )
            
            # Add to recipient's bucket at current rate
            recipient_wallet.fiat_balance_by_rate = _add_to_bucket(
                recipient_wallet.fiat_balance_by_rate or {}, recipient_rate_key, send_amount
            )
            
            # Trigger Bridge wallet-to-wallet transfer
            client = BridgeClient()
            usdc_amount = send_amount * sender_rate
            bridge_transfer = client.create_transfer_sync({
                "amount": str(usdc_amount),  # Convert to USDC amount
                "on_behalf_of": sender_wallet.customer_id,
                "source": {
                    "payment_rail": "bridge_wallet",
                    "bridge_wallet_id": sender_wallet.wallet_id,
                    "currency": "usdc"
                },
                "destination": {
                    "payment_rail": "solana",
                    "to_address": recipient_wallet.address,
                    "currency": "usdc"
                }
            })
            
            db.commit()
            
            return SendOut(
                transfer_id=bridge_transfer.get("id", str(uuid.uuid4())),
                status="completed",
                sender_currency=sender_currency,
                recipient_currency=recipient_currency,
                amount_sent=float(send_amount),
                amount_received=float(send_amount),
                exchange_rate=1.0
            )
            
        else:
            # Case 6: Cross-currency send (C₁ → C₂)
            
            # Convert sender amount to USDC
            usdc_amount = send_amount * sender_rate
            
            # Convert USDC to recipient currency
            recipient_amount = usdc_amount / recipient_rate
            
            # Deduct from sender's buckets
            sender_wallet.fiat_balance_by_rate = _deduct_from_buckets(
                sender_wallet.fiat_balance_by_rate or {}, send_amount
            )
            
            # Add to recipient's bucket at current rate
            recipient_wallet.fiat_balance_by_rate = _add_to_bucket(
                recipient_wallet.fiat_balance_by_rate or {}, recipient_rate_key, recipient_amount
            )
            
            # Trigger Bridge wallet-to-wallet transfer
            client = BridgeClient()
            bridge_transfer = client.create_transfer_sync({
                "amount": str(usdc_amount),
                "on_behalf_of": sender_wallet.customer_id,
                "source": {
                    "payment_rail": "bridge_wallet",
                    "bridge_wallet_id": sender_wallet.wallet_id,
                    "currency": "usdc"
                },
                "destination": {
                    "payment_rail": "solana",
                    "to_address": recipient_wallet.address,
                    "currency": "usdc"
                }
            })
            
            db.commit()
            
            return SendOut(
                transfer_id=bridge_transfer.get("id", str(uuid.uuid4())),
                status="completed",
                sender_currency=sender_currency,
                recipient_currency=recipient_currency,
                amount_sent=float(send_amount),
                amount_received=float(recipient_amount),
                exchange_rate=float(recipient_amount / send_amount)
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

    if not CORPORATE_WALLET_ID or not CORPORATE_CUSTOMER_ID:
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
    rail_by_cur = {"usd": "ach_push", "eur": "sepa", "mxn": "spei"}
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
        treas_wallet = client.get_wallet(CORPORATE_CUSTOMER_ID, CORPORATE_WALLET_ID)
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
            "bridge_wallet_id": CORPORATE_WALLET_ID,
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
        "on_behalf_of": CORPORATE_CUSTOMER_ID,  # treasury sends on its own behalf
        "source": {
            "payment_rail": "solana",
            "currency": "usdb",
            "bridge_wallet_id": CORPORATE_WALLET_ID,
        },
        "destination": {
            "payment_rail": "solana",
            "currency": "usdb",
            "bridge_wallet_id": bridge_wallet.id,
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
        user_wallet_id=bridge_wallet.id,
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


@router.post("/withdraw", response_model=Dict[str, Any])
async def withdraw_fiat_from_wallet(
    body: WithdrawalIn,
    db: Session = Depends(get_db),
    auth_user: Auth0User = Depends(get_current_user),
):
    """Initiate a fiat withdrawal: Bridge wallet ➜ external bank account.

    We pick the appropriate fiat rail (ACH, SEPA, etc.) based on the external
    account's currency.
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

    client = BridgeClient()

    # Fetch external account to validate ownership & get currency
    try:
        ext_acct = client.get_external_account(body.external_account_id, bridge_customer.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid external account: {e}")

    currency = (ext_acct.get("currency") or "usd").lower()
    rail_by_cur = {"usd": "ach_push", "eur": "sepa"}
    if currency not in rail_by_cur:
        raise HTTPException(status_code=400, detail=f"Unsupported withdrawal currency: {currency}")

    payment_rail = rail_by_cur[currency]

    payload = {
        "amount": str(body.amount),
        "on_behalf_of": bridge_customer.id,
        "source": {
            "payment_rail": "solana",
            "currency": "usdb",
            "wallet_id": bridge_wallet.id,
        },
        "destination": {
            "payment_rail": payment_rail,
            "currency": currency,
            "external_account_id": body.external_account_id,
        },
    }

    try:
        transfer = client.create_transfer_sync(payload)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Bridge withdrawal failed: {e}")

    # TODO: optionally persist withdrawal record / encumbrance if needed
    return transfer 