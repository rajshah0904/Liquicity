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
from app.utils.fee_constants import (
    STANDARD_SEND_FEE_PCT,
    BANK_TRANSFER_FEE_PCT,
    INSTANT_DEPOSIT_FEE_PCT
)

router = APIRouter(prefix="/transfer", tags=["transfer"])

# -------------------------------
# Helper utilities
# -------------------------------

def _lookup_user(db: Session, identifier: str):
    return db.execute(
        text("SELECT id, bridge_customer_id FROM users WHERE email = :id OR auth0_id = :id"),
        {"id": identifier},
    ).first()

async def _get_wallet_by_currency(client: BridgeClient, customer_id: str, currency: str = None) -> str:
    """Get wallet ID for a customer based on currency."""
    wallets = await client.get_wallets(customer_id)
    if not wallets:
        raise HTTPException(status_code=400, detail=f"User has no wallets on Bridge")
        
    # If no currency specified, return the first wallet
    if not currency:
        if len(wallets) > 0:
            return wallets[0].get("id")
        raise HTTPException(status_code=400, detail="User has no wallets on Bridge")
        
    # Look for wallet with specified currency
    currency = currency.lower()
    for w in wallets:
        if w.get("currency") == currency:
            return w.get("id")
            
    # If no matching currency wallet exists, raise an error
    raise HTTPException(status_code=400, detail=f"User has no {currency.upper()} wallet on Bridge")

TREASURY_WALLET_ID = os.getenv("TREASURY_WALLET_ID")
if not TREASURY_WALLET_ID:
    print("⚠️ TREASURY_WALLET_ID not set – advance payouts will be disabled.")

# -------------------------------
# Request models
# -------------------------------

class InternalTransferIn(BaseModel):
    recipient_user_id: int = Field(..., description="DB id of the recipient user")
    amount: condecimal(gt=Decimal("0"), max_digits=18, decimal_places=2) = Field(..., description="Amount in USDB to transfer")

class DepositIn(BaseModel):
    amount: condecimal(gt=Decimal("0"), max_digits=18, decimal_places=2)
    external_account_id: str = Field(..., description="Bridge external_account_id to debit")
    instant: bool = Field(False, description="If true, company advances funds from treasury for instant credit")

# -------------------------------
# New request models for send & withdraw
# -------------------------------

class SendIn(BaseModel):
    recipient_user_id: int
    amount: condecimal(gt=Decimal("0"), max_digits=18, decimal_places=2)
    speed_option: str = Field("standard", description="Speed option: 'standard' or 'express'")
    # For partial transactions (when wallet funds are insufficient)
    amount_from_wallet: condecimal(ge=Decimal("0"), max_digits=18, decimal_places=2) = None
    amount_from_bank: condecimal(ge=Decimal("0"), max_digits=18, decimal_places=2) = None
    # Optional external account to pull fiat when insufficient funds
    external_account_id: str | None = Field(None, description="Sender's external_account_id used if wallet funds insufficient")

class WithdrawIn(BaseModel):
    amount: condecimal(gt=Decimal("0"), max_digits=18, decimal_places=2)
    external_account_id: str

class SendPaymentRequest(BaseModel):
    """Send payment request body model."""
    recipient_user_id: str = Field(..., description="Liquicity user ID of the payment recipient")
    amount: condecimal(gt=Decimal("0"), max_digits=18, decimal_places=2) = Field(..., description="Amount to transfer")
    description: str = Field(None, description="Optional payment description or note")

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
    sender_wallet_id   = await _get_wallet_by_currency(client, sender_cust_id)
    recipient_wallet_id = await _get_wallet_by_currency(client, recipient_cust_id)

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

def _get_user_currency(db: Session, user_id: int) -> str:
    """Get the user's currency based on their country from KYC/profile."""
    row = db.execute(
        text("SELECT country FROM users WHERE id = :uid"),
        {"uid": user_id}
    ).first()
    
    if not row or not row[0]:
        return "usd"  # Default to USD if country not found
    
    country = row[0].upper()
    
    # Map country to currency
    if country == "MX":
        return "mxn"
    elif country in [
        "AT","BE","BG","CH","CY","CZ","DE","DK","EE","ES","FI","FR","GB",
        "GR","HR","HU","IE","IS","IT","LI","LT","LU","LV","MT","NL","NO",
        "PL","PT","RO","SE","SI","SK"
    ]:
        return "eur"
    else:
        return "usd"  # Default to USD for other countries

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
    user_id, cust_id = user_row

    # Get user's currency from profile/KYC
    user_currency = _get_user_currency(db, user_id)
    
    client = BridgeClient()
    user_wallet_id = await _get_wallet_by_currency(client, cust_id)

    # Step 1: create fiat->stable on-ramp transfer
    fiat_payload: Dict[str, Any] = {
        "amount": str(body.amount),
        "on_behalf_of": cust_id,
        "source": {
            "payment_rail": "sepa" if user_currency == "eur" else ("spei" if user_currency == "mxn" else "ach"),
            "currency": user_currency,
            "external_account_id": body.external_account_id,
        },
        "destination": {
            "payment_rail": "polygon",
            "currency": user_currency,
            "wallet_id": user_wallet_id,
        },
        "convert_to_currency": user_currency,
    }
    try:
        create_resp = await client.create_transfer(fiat_payload)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to initiate on-ramp: {e}")

    instant_details = None
    if body.instant:
        # Use the updated instant deposit fee (1.5076%)
        dev_fee = (Decimal(body.amount) * INSTANT_DEPOSIT_FEE_PCT).quantize(Decimal("0.01"))
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
    """Peer-to-peer send with two speed options:
    
    Standard: Slow deposit (0%) + P2P send (0.5%); all-in = 0.5%
    Express: Instant deposit (1.5076%) + P2P send (0.5%); all-in = 2.0%
    
    If sender funds are insufficient:
    - Standard: Part from wallet (instant) + part from bank (1-3 days)
    - Express: All funds advanced instantly with 2.0% fee
    """
    sender_row = _lookup_user(db, current_user)
    if not sender_row or not sender_row[1]:
        raise HTTPException(status_code=404, detail="Sender missing Bridge account")
    sender_id, sender_cust_id = sender_row

    # Get sender's currency from profile/KYC
    sender_currency = _get_user_currency(db, sender_id)
    
    rec_row = db.execute(text("SELECT id, bridge_customer_id FROM users WHERE id = :rid"), {"rid": body.recipient_user_id}).first()
    if not rec_row or not rec_row[1]:
        raise HTTPException(status_code=404, detail="Recipient missing Bridge account")
    recipient_id, recipient_cust_id = rec_row

    # Get recipient's currency from profile/KYC
    recipient_currency = _get_user_currency(db, recipient_id)
    
    client = BridgeClient()
    sender_wallet_id = await _get_wallet_by_currency(client, sender_cust_id, sender_currency)
    recipient_wallet_id = await _get_wallet_by_currency(client, recipient_cust_id, recipient_currency)

    # Balance check
    wallets = await client.list_wallets(sender_cust_id)
    balance = Decimal("0")
    for w in wallets:
        if w.get("id") == sender_wallet_id:
            balance = Decimal(str(w.get("balance", "0")))
            break

    # Get the total amount to send
    total_amount = body.amount
    
    # Determine transfer handling based on speed option and available balance
    if body.speed_option == "standard":
        # Standard option: 0.5% all-in fee
        # If insufficient funds, split into two parts:
        # 1. Wallet → Wallet transfer (instant, 0.5% fee)
        # 2. Bank → Wallet transfer (1-3 days, 0.5% fee)
        
        if balance >= total_amount:
            # Sufficient funds: simple wallet-to-wallet transfer
            fee = (total_amount * STANDARD_SEND_FEE_PCT).quantize(Decimal("0.01"))
            payload = {
                "amount": str(total_amount),
                "developer_fee": str(fee),
                "on_behalf_of": sender_cust_id,
                "source": {"payment_rail": "polygon", "currency": sender_currency, "wallet_id": sender_wallet_id},
                "destination": {"payment_rail": "polygon", "currency": recipient_currency, "wallet_id": recipient_wallet_id},
            }
            try:
                resp = await client.create_transfer(payload)
            except Exception as e:
                raise HTTPException(status_code=502, detail=f"Bridge transfer failed: {e}")
            
            return {
                "success": True, 
                "covered": True, 
                "fee": str(fee), 
                "transfer_id": resp.get("id"), 
                "state": resp.get("state"),
                "speed_option": "standard"
            }
        else:
            # Insufficient funds: split into two parts
            # 1. Transfer what's available in wallet (instant)
            if balance > Decimal("0"):
                wallet_fee = (balance * STANDARD_SEND_FEE_PCT).quantize(Decimal("0.01"))
                wallet_payload = {
                    "amount": str(balance),
                    "developer_fee": str(wallet_fee),
                    "on_behalf_of": sender_cust_id,
                    "source": {"payment_rail": "polygon", "currency": sender_currency, "wallet_id": sender_wallet_id},
                    "destination": {"payment_rail": "polygon", "currency": recipient_currency, "wallet_id": recipient_wallet_id},
                }
                try:
                    wallet_resp = await client.create_transfer(wallet_payload)
                except Exception as e:
                    raise HTTPException(status_code=502, detail=f"Bridge transfer from wallet failed: {e}")
            
            # 2. Bank transfer for remaining amount (1-3 days)
            remaining_amount = total_amount - balance
            if remaining_amount > Decimal("0"):
                if not body.external_account_id:
                    raise HTTPException(status_code=400, detail={
                        "error": "insufficient_funds",
                        "available_balance": str(balance),
                        "message": "Wallet balance insufficient. Provide external_account_id to fund transfer.",
                    })
                
                # Standard deposit from bank (no fee) + P2P send (0.5% fee)
                bank_fee = (remaining_amount * STANDARD_SEND_FEE_PCT).quantize(Decimal("0.01"))
                
                # Initiate standard bank pull to recipient wallet (takes 1-3 days)
                bank_payload = {
                    "amount": str(remaining_amount),
                    "developer_fee": str(bank_fee),
                    "on_behalf_of": sender_cust_id,
                    "source": {
                        "payment_rail": "sepa" if sender_currency == "eur" else ("spei" if sender_currency == "mxn" else "ach"),
                        "currency": sender_currency,
                        "external_account_id": body.external_account_id,
                    },
                    "destination": {
                        "payment_rail": "polygon",
                        "currency": recipient_currency,
                        "wallet_id": recipient_wallet_id,
                    },
                    "convert_to_currency": recipient_currency,
                }
                try:
                    bank_resp = await client.create_transfer(bank_payload)
                except Exception as e:
                    raise HTTPException(status_code=502, detail=f"Bridge transfer from bank failed: {e}")
            
            # Return combined result
            return {
                "success": True,
                "covered": False,
                "split_transaction": True,
                "wallet_amount": str(balance),
                "bank_amount": str(remaining_amount if remaining_amount > Decimal("0") else Decimal("0")),
                "total_fee": str((wallet_fee if 'wallet_fee' in locals() else Decimal("0")) + 
                                 (bank_fee if 'bank_fee' in locals() else Decimal("0"))),
                "wallet_transfer_id": wallet_resp.get("id") if balance > Decimal("0") else None,
                "bank_transfer_id": bank_resp.get("id") if remaining_amount > Decimal("0") else None,
                "speed_option": "standard"
            }
    
    else:  # Express option: 2.0% all-in fee, always instant
        # Express = Instant deposit (1.5076%) + P2P send (0.5%)
        # All funds advanced instantly regardless of balance
        
        # Calculate the 2.0% all-in express fee
        express_fee_rate = Decimal("0.02")  # 2.0%
        express_fee = (total_amount * express_fee_rate).quantize(Decimal("0.01"))
        
        if balance >= total_amount:
            # If sufficient balance, just do a wallet transfer with 2.0% fee
            payload = {
                "amount": str(total_amount),
                "developer_fee": str(express_fee),
                "on_behalf_of": sender_cust_id,
                "source": {"payment_rail": "polygon", "currency": sender_currency, "wallet_id": sender_wallet_id},
                "destination": {"payment_rail": "polygon", "currency": recipient_currency, "wallet_id": recipient_wallet_id},
            }
            try:
                resp = await client.create_transfer(payload)
            except Exception as e:
                raise HTTPException(status_code=502, detail=f"Bridge express transfer failed: {e}")
            
            return {
                "success": True,
                "covered": True,
                "fee": str(express_fee),
                "transfer_id": resp.get("id"),
                "state": resp.get("state"),
                "speed_option": "express"
            }
        else:
            # For insufficient funds with Express option:
            # 1. Transfer what's available in wallet
            if balance > Decimal("0"):
                # Calculate prorated fee for wallet portion
                wallet_portion_fee = (balance * express_fee_rate).quantize(Decimal("0.01"))
                wallet_payload = {
                    "amount": str(balance),
                    "developer_fee": str(wallet_portion_fee),
                    "on_behalf_of": sender_cust_id,
                    "source": {"payment_rail": "polygon", "currency": sender_currency, "wallet_id": sender_wallet_id},
                    "destination": {"payment_rail": "polygon", "currency": recipient_currency, "wallet_id": recipient_wallet_id},
                }
                try:
                    wallet_resp = await client.create_transfer(wallet_payload)
                except Exception as e:
                    raise HTTPException(status_code=502, detail=f"Bridge express wallet transfer failed: {e}")
            
            # 2. Advance the remaining amount from treasury with instant deposit
            remaining_amount = total_amount - balance
            if remaining_amount > Decimal("0"):
                if not body.external_account_id:
                    raise HTTPException(status_code=400, detail={
                        "error": "insufficient_funds",
                        "available_balance": str(balance),
                        "message": "Wallet balance insufficient. Provide external_account_id for express transfer.",
                    })
                
                # Initiate instant deposit + bank pull to treasury
                bank_portion_fee = (remaining_amount * express_fee_rate).quantize(Decimal("0.01"))
                
                # Pull from bank to treasury
                treasury_wallet_id = _get_treasury_wallet_id()
                bank_payload = {
                    "amount": str(remaining_amount),
                    "on_behalf_of": sender_cust_id,
                    "source": {
                        "payment_rail": "sepa" if sender_currency == "eur" else ("spei" if sender_currency == "mxn" else "ach"),
                        "currency": sender_currency,
                        "external_account_id": body.external_account_id,
                    },
                    "destination": {
                        "payment_rail": "polygon",
                        "currency": sender_currency,
                        "wallet_id": treasury_wallet_id,
                    },
                    "convert_to_currency": sender_currency,
                }
                try:
                    bank_resp = await client.create_transfer(bank_payload)
                except Exception as e:
                    raise HTTPException(status_code=502, detail=f"Failed to start express funding transfer: {e}")
                
                # Advance from treasury to recipient instantly
                try:
                    advance_resp = await _credit_from_treasury(
                        client, recipient_wallet_id, remaining_amount, 
                        sender_cust_id, developer_fee=bank_portion_fee
                    )
                except Exception as e:
                    raise HTTPException(status_code=502, detail=f"Failed to advance express funds: {e}")
            
            # Return combined result
            return {
                "success": True,
                "covered": False,
                "express": True,
                "wallet_amount": str(balance),
                "advanced_amount": str(remaining_amount if remaining_amount > Decimal("0") else Decimal("0")),
                "total_fee": str((wallet_portion_fee if 'wallet_portion_fee' in locals() else Decimal("0")) + 
                                 (bank_portion_fee if 'bank_portion_fee' in locals() else Decimal("0"))),
                "wallet_transfer_id": wallet_resp.get("id") if balance > Decimal("0") else None,
                "bank_transfer_id": bank_resp.get("id") if remaining_amount > Decimal("0") else None,
                "advance_transfer_id": advance_resp.get("id") if remaining_amount > Decimal("0") else None,
                "speed_option": "express"
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
    user_id, cust_id = user_row

    # Get user's currency from profile/KYC
    user_currency = _get_user_currency(db, user_id)
    
    client = BridgeClient()
    wallet_id = await _get_wallet_by_currency(client, cust_id)

    off_payload = {
        "amount": str(body.amount),
        "on_behalf_of": cust_id,
        "source": {"payment_rail": "polygon", "currency": user_currency, "wallet_id": wallet_id},
        "destination": {
            "payment_rail": "sepa" if user_currency == "eur" else ("spei" if user_currency == "mxn" else "ach"),
            "currency": user_currency,
            "external_account_id": body.external_account_id,
        },
        "convert_to_currency": user_currency,
    }
    try:
        resp = await client.create_transfer(off_payload)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Off-ramp failed: {e}")
    return {"success": True, "transfer_id": resp.get("id"), "state": resp.get("state")} 