from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, condecimal
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
from typing import Dict, Any, List
import os

from app.dependencies.auth import get_current_user
from app.database import get_db
from app.services.bridge import BridgeClient

router = APIRouter(prefix="/transfer", tags=["transfer"])

# -------------------------------
# Helper utilities
# -------------------------------

def _lookup_user(db: Session, identifier: str):
    return db.execute(
        text("SELECT id, bridge_customer_id FROM users WHERE email = :id OR auth0_id = :id"),
        {"id": identifier},
    ).first()

async def _get_usdb_wallet_id(client: BridgeClient, customer_id: str) -> str:
    wallets: List[Dict[str, Any]] = await client.list_wallets(customer_id)
    for w in wallets:
        if w.get("currency") == "usdb":
            return w.get("id")
    raise HTTPException(status_code=400, detail="User has no USDB wallet on Bridge")

TREASURY_WALLET_ID = os.getenv("TREASURY_WALLET_ID")
if not TREASURY_WALLET_ID:
    print("⚠️ TREASURY_WALLET_ID not set – advance payouts will be disabled.")

SEND_COVERED_FEE_PCT = Decimal(os.getenv("SEND_COVERED_FEE_PCT", "0.005"))  # 0.5%
SEND_UNCOVERED_FEE_PCT = Decimal(os.getenv("SEND_UNCOVERED_FEE_PCT", "0.03"))  # 3%

# -------------------------------
# Request models
# -------------------------------

class InternalTransferIn(BaseModel):
    recipient_user_id: int = Field(..., description="DB id of the recipient user")
    amount: condecimal(gt=Decimal("0"), max_digits=18, decimal_places=2) = Field(..., description="Amount in USDB to transfer")

class DepositIn(BaseModel):
    amount: condecimal(gt=Decimal("0"), max_digits=18, decimal_places=2)
    currency: str = Field("eur", description="Fiat currency being debited: usd, eur, mxn")
    external_account_id: str = Field(..., description="Bridge external_account_id to debit")
    instant: bool = Field(False, description="If true, company advances funds from treasury for instant credit")

# -------------------------------
# New request models for send & withdraw
# -------------------------------

class SendIn(BaseModel):
    recipient_user_id: int
    amount: condecimal(gt=Decimal("0"), max_digits=18, decimal_places=2)
    # Optional external account to pull fiat when insufficient funds
    external_account_id: str | None = Field(None, description="Sender's external_account_id used if wallet funds insufficient")
    currency: str | None = Field(None, description="Currency of external account (usd, eur, mxn). Required if external_account_id supplied.")

class WithdrawIn(BaseModel):
    amount: condecimal(gt=Decimal("0"), max_digits=18, decimal_places=2)
    external_account_id: str
    currency: str  # fiat currency of bank account (usd, eur, mxn)

# -------------------------------
# Endpoints
# -------------------------------

@router.post("/internal")
async def internal_wallet_transfer(
    body: InternalTransferIn,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Move USDB from the authenticated sender's wallet to another Liquicity user's wallet.
    No treasury involvement, purely wallet → wallet on Polygon (or Bridge default chain).
    """
    # Lookup sender
    sender_row = _lookup_user(db, current_user)
    if not sender_row or not sender_row[1]:
        raise HTTPException(status_code=404, detail="Sender does not have a Bridge account")
    sender_id, sender_cust_id = sender_row

    # Lookup recipient
    rec_row = db.execute(text("SELECT bridge_customer_id FROM users WHERE id = :rid"), {"rid": body.recipient_user_id}).first()
    if not rec_row or not rec_row[0]:
        raise HTTPException(status_code=404, detail="Recipient does not have a Bridge account")
    recipient_cust_id = rec_row[0]

    client = BridgeClient()

    # Fetch wallets
    sender_wallet_id   = await _get_usdb_wallet_id(client, sender_cust_id)
    recipient_wallet_id = await _get_usdb_wallet_id(client, recipient_cust_id)

    # Optional: basic balance check
    sender_wallets = await client.wallet_history(sender_wallet_id)  # history endpoint returns txns, not balance; need list_wallets for balance
    wallets = await client.list_wallets(sender_cust_id)
    balance: Decimal = Decimal("0")
    for w in wallets:
        if w.get("id") == sender_wallet_id:
            balance = Decimal(str(w.get("balance", "0")))
            break
    if balance < body.amount:
        raise HTTPException(status_code=400, detail={
            "error": "insufficient_funds",
            "available_balance": str(balance),
            "message": "Not enough USDB to complete transfer. Please deposit funds via ACH, SEPA, or SPEI."
        })

    # Build Bridge transfer payload
    payload: Dict[str, Any] = {
        "amount": str(body.amount),
        "on_behalf_of": sender_cust_id,
        "source": {
            "payment_rail": "polygon",
            "currency": "usdb",
            "wallet_id": sender_wallet_id,
        },
        "destination": {
            "payment_rail": "polygon",
            "currency": "usdb",
            "wallet_id": recipient_wallet_id,
        },
    }

    try:
        resp = await client.create_transfer(payload)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Bridge transfer failed: {e}")

    # Optionally persist to local transfers table later

    return {
        "success": True,
        "transfer_id": resp.get("id"),
        "state": resp.get("state"),
    } 

# -------------------------------
# Utility
# -------------------------------

def _get_treasury_wallet_id() -> str:
    if not TREASURY_WALLET_ID:
        raise HTTPException(status_code=500, detail="Treasury wallet not configured on server")
    return TREASURY_WALLET_ID

async def _credit_from_treasury(client: BridgeClient, recipient_wallet_id: str, amount: Decimal, on_behalf_of: str, developer_fee: Decimal = Decimal("0")):
    """Send USDB from corporate treasury wallet to recipient with optional developer fee."""
    payload = {
        "amount": str(amount),
        "on_behalf_of": on_behalf_of,
        "source": {
            "payment_rail": "polygon",
            "currency": "usdb",
            "wallet_id": _get_treasury_wallet_id(),
        },
        "destination": {
            "payment_rail": "polygon",
            "currency": "usdb",
            "wallet_id": recipient_wallet_id,
        },
    }
    if developer_fee and developer_fee > 0:
        payload["developer_fee"] = str(developer_fee)
    return await client.create_transfer(payload)

# -------------------------------
# Deposit endpoint
# -------------------------------

@router.post("/deposit")
async def deposit_fiat_to_wallet(
    body: DepositIn,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Initiate fiat on-ramp to user wallet. Optionally perform instant credit by advancing from treasury."""
    # Look up user and wallet
    user_row = _lookup_user(db, current_user)
    if not user_row or not user_row[1]:
        raise HTTPException(status_code=404, detail="User not found or not KYCd")
    _, cust_id = user_row

    client = BridgeClient()
    user_wallet_id = await _get_usdb_wallet_id(client, cust_id)

    # Step 1: create fiat->stable on-ramp transfer
    fiat_payload: Dict[str, Any] = {
        "amount": str(body.amount),
        "on_behalf_of": cust_id,
        "source": {
            "payment_rail": "sepa" if body.currency.lower() == "eur" else ("spei" if body.currency.lower() == "mxn" else "ach"),
            "currency": body.currency.lower(),
            "external_account_id": body.external_account_id,
        },
        "destination": {
            "payment_rail": "polygon",
            "currency": "usdb",
            "wallet_id": user_wallet_id,
        },
        "convert_to_currency": "usd",
    }
    try:
        create_resp = await client.create_transfer(fiat_payload)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to initiate on-ramp: {e}")

    instant_details = None
    if body.instant:
        # Compute fee (e.g., 1% of amount) and include developer_fee in advance transfer
        fee_pct = Decimal(os.getenv("INSTANT_DEPOSIT_FEE_PCT", "0.01"))
        dev_fee = (Decimal(body.amount) * fee_pct).quantize(Decimal("0.01"))
        try:
            adv_resp = await _credit_from_treasury(client, user_wallet_id, Decimal(body.amount), cust_id, dev_fee)
            instant_details = {
                "advance_transfer_id": adv_resp.get("id"),
                "state": adv_resp.get("state"),
                "developer_fee": str(dev_fee),
            }
        except Exception as e:
            # If advance fails we still proceed with normal settlement, but notify front-end.
            instant_details = {"error": str(e)}

    return {
        "on_ramp_transfer_id": create_resp.get("id"),
        "state": create_resp.get("state"),
        "instant": bool(body.instant),
        "instant_details": instant_details,
    } 

# -------------------------------
# Send endpoint
# -------------------------------

@router.post("/send")
async def send_money(
    body: SendIn,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Peer-to-peer send. If sender funds sufficient, USDB wallet→wallet (0.5% fee).
    If insufficient, trigger on-ramp to treasury and advance funds to recipient (3% fee).
    """
    sender_row = _lookup_user(db, current_user)
    if not sender_row or not sender_row[1]:
        raise HTTPException(status_code=404, detail="Sender missing Bridge account")
    sender_id, sender_cust_id = sender_row

    rec_row = db.execute(text("SELECT bridge_customer_id FROM users WHERE id = :rid"), {"rid": body.recipient_user_id}).first()
    if not rec_row or not rec_row[0]:
        raise HTTPException(status_code=404, detail="Recipient missing Bridge account")
    recipient_cust_id = rec_row[0]

    client = BridgeClient()
    sender_wallet_id = await _get_usdb_wallet_id(client, sender_cust_id)
    recipient_wallet_id = await _get_usdb_wallet_id(client, recipient_cust_id)

    # Balance check
    wallets = await client.list_wallets(sender_cust_id)
    balance = Decimal("0")
    for w in wallets:
        if w.get("id") == sender_wallet_id:
            balance = Decimal(str(w.get("balance", "0")))
            break

    if balance >= body.amount:
        # Covered transfer with 0.5% fee
        fee = (Decimal(body.amount) * SEND_COVERED_FEE_PCT).quantize(Decimal("0.01"))
        payload = {
            "amount": str(body.amount),
            "developer_fee": str(fee),
            "on_behalf_of": sender_cust_id,
            "source": {"payment_rail": "polygon", "currency": "usdb", "wallet_id": sender_wallet_id},
            "destination": {"payment_rail": "polygon", "currency": "usdb", "wallet_id": recipient_wallet_id},
        }
        try:
            resp = await client.create_transfer(payload)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Bridge transfer failed: {e}")
        return {"success": True, "covered": True, "fee": str(fee), "transfer_id": resp.get("id"), "state": resp.get("state")}

    # Not covered – need external transfer info
    if not body.external_account_id or not body.currency:
        raise HTTPException(status_code=400, detail={
            "error": "insufficient_funds",
            "available_balance": str(balance),
            "message": "Wallet balance insufficient. Provide external_account_id and currency to fund transfer.",
        })

    # 1. Initiate bank pull to treasury wallet
    treasury_wallet_id = _get_treasury_wallet_id()
    fiat_payload = {
        "amount": str(body.amount),
        "on_behalf_of": sender_cust_id,
        "source": {
            "payment_rail": "sepa" if body.currency.lower() == "eur" else ("spei" if body.currency.lower() == "mxn" else "ach"),
            "currency": body.currency.lower(),
            "external_account_id": body.external_account_id,
        },
        "destination": {
            "payment_rail": "polygon",
            "currency": "usdb",
            "wallet_id": treasury_wallet_id,
        },
        "convert_to_currency": "usd",
    }
    try:
        onramp_resp = await client.create_transfer(fiat_payload)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to start funding transfer: {e}")

    # 2. Advance funds from treasury to recipient (3% fee)
    adv_fee = (Decimal(body.amount) * SEND_UNCOVERED_FEE_PCT).quantize(Decimal("0.01"))
    try:
        advance_resp = await _credit_from_treasury(client, recipient_wallet_id, Decimal(body.amount), sender_cust_id, developer_fee=adv_fee)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to advance funds: {e}")

    return {
        "success": True,
        "covered": False,
        "fee": str(adv_fee),
        "on_ramp_transfer_id": onramp_resp.get("id"),
        "advance_transfer_id": advance_resp.get("id"),
        "state": advance_resp.get("state"),
    }

# -------------------------------
# Withdraw endpoint
# -------------------------------

@router.post("/withdraw")
async def withdraw_funds(
    body: WithdrawIn,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Stablecoin → Fiat off-ramp (always 1-3 business days, no fee)."""
    user_row = _lookup_user(db, current_user)
    if not user_row or not user_row[1]:
        raise HTTPException(status_code=404, detail="User not found")
    _, cust_id = user_row

    client = BridgeClient()
    wallet_id = await _get_usdb_wallet_id(client, cust_id)

    off_payload = {
        "amount": str(body.amount),
        "on_behalf_of": cust_id,
        "source": {"payment_rail": "polygon", "currency": "usdb", "wallet_id": wallet_id},
        "destination": {
            "payment_rail": "sepa" if body.currency.lower() == "eur" else ("spei" if body.currency.lower() == "mxn" else "ach"),
            "currency": body.currency.lower(),
            "external_account_id": body.external_account_id,
        },
        "convert_to_currency": body.currency.lower(),
    }
    try:
        resp = await client.create_transfer(off_payload)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Off-ramp failed: {e}")
    return {"success": True, "transfer_id": resp.get("id"), "state": resp.get("state")} 