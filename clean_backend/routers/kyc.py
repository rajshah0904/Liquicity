from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models import User, BridgeCustomer, BridgeWallet
from ..bridge import BridgeClient
from ..auth import get_current_user
from ..utils.currency_utils import get_fiat_currency_from_region
import logging
import json
import datetime
import os

router = APIRouter(prefix="/kyc", tags=["kyc"])
_log = logging.getLogger(__name__)


def _lookup_user(db: Session, sub: str) -> Optional[User]:
    """Look up user by Auth0 subject ID only - NEVER by email to prevent auth bugs"""
    return db.query(User).filter(User.auth0_id == sub).first()


@router.post("/tos_link")
async def generate_tos_link(request: Request, db: Session = Depends(get_db), jwt=Depends(get_current_user)):
    """Generate a Bridge Terms of Service link that redirects back to the KYC page with signed_agreement_id."""
    user = _lookup_user(db, getattr(jwt, 'id', None))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    app_url = os.getenv("APP_URL", f"{request.url.scheme}://{request.url.hostname}:3000")
    try:
        tos = BridgeClient().request_tos_links(redirect_uri=f"{app_url}/kyc-verification")
        # Expected response: { "url": "https://dashboard.bridge.xyz/accept-terms-of-service?session_token=..." }
        return tos
    except Exception as e:
        _log.error("request_tos_links failed: %s", e)
        raise HTTPException(status_code=502, detail="Bridge request_tos_links failed")


@router.post("/link")
async def generate_kyc_link(db: Session = Depends(get_db), jwt=Depends(get_current_user)):
    user = _lookup_user(db, getattr(jwt, 'id', None))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.email:
        raise HTTPException(status_code=400, detail="Email required for KYC link generation")

    link = BridgeClient().create_kyc_link({
        "type": "individual",
        "email": user.email,
        "endorsements": ["sepa"],
    })

    # Note: kyc_link_id and kyc_url fields removed from User model
    # Store link details in session or return directly
    return link


@router.post("/callback", include_in_schema=False)
async def kyc_callback(request: Request, db: Session = Depends(get_db)):
    """Endpoint Bridge calls with KYC status updates"""
    body = await request.json()
    cid = body.get("customer_id")
    status = body.get("kyc_status")
    kyc_link_id = body.get("id")
    tos_status = body.get("tos_status")
    rejection_reasons = body.get("rejection_reasons")

    # Find user by bridge customer id
    user = None
    if cid:
        bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.id == cid).first()
        if bridge_customer:
            user = db.query(User).filter(User.id == bridge_customer.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Note: kyc_status, tos_status, rejection_reasons fields removed from User model
    # For now, just log the status
    _log.info(f"KYC callback for user {user.id}: status={status}, tos_status={tos_status}")

    if status == "approved":
        # When approved, create customer and wallet if they don't exist
        bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == user.id).first()
        
        if not bridge_customer:
            try:
                customer = BridgeClient().create_customer({
                    "type": "individual",
                    "email": user.email,
                })
                
                # Create BridgeCustomer record
                bridge_customer = BridgeCustomer(
                    id=customer.get("id"),
                    user_id=user.id,
                    first_name=customer.get("first_name"),
                    last_name=customer.get("last_name"),
                    email=customer.get("email"),
                    status=customer.get("status", "active"),
                    country=customer.get("country"),
                    created_at=datetime.datetime.utcnow(),
                    updated_at=datetime.datetime.utcnow()
                )
                db.add(bridge_customer)
                db.flush()
                
                _log.info(f"Created Bridge customer {bridge_customer.id} for user {user.id}")
            except Exception as e:
                _log.error("create_customer failed: %s", e)
                raise HTTPException(status_code=502, detail="Failed to create Bridge customer")

        # Create wallet if it doesn't exist
        bridge_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == user.id).first()
        if not bridge_wallet and bridge_customer:
            try:
                wallet = BridgeClient().create_wallet(bridge_customer.id, chain="solana")
                
                # Create BridgeWallet record with fiat currency mapping
                fiat_currency = get_fiat_currency_from_region(user.region) if user.region else 'USD'
                
                bridge_wallet = BridgeWallet(
                    wallet_id=wallet.get("id"),
                    user_id=user.id,
                    customer_id=bridge_customer.id,
                    chain=wallet.get("chain", "solana"),
                    address=wallet.get("address"),
                    balances=wallet.get("balances", []),
                    fiat_currency=fiat_currency,
                    fiat_balance_by_rate={},
                    created_at=datetime.datetime.utcnow(),
                    updated_at=datetime.datetime.utcnow()
                )
                db.add(bridge_wallet)
                db.flush()
                
                _log.info(f"Created Bridge wallet {bridge_wallet.id} for user {user.id}")
                
            except Exception as e:
                _log.error("create_wallet failed: %s", e)
                # Non-fatal - wallet creation can be retried later
    elif status == "rejected":
        _log.info("User %s KYC rejected", user.id)
    else:
        # incomplete, under_review etc.
        pass

    db.commit()
    return {"status": "ok"}


@router.get("/status")
async def get_kyc_status(db: Session = Depends(get_db), jwt: dict = Depends(get_current_user)):
    user = db.query(User).filter(User.auth0_id == jwt.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user has Bridge customer and wallet (indicates KYC completion)
    bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == user.id).first()
    bridge_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == user.id).first()
    
    # Determine KYC status based on Bridge customer existence
    kyc_status = "approved" if bridge_customer else "pending"
    
    return {
        "kyc_status": kyc_status,
        "link_status": kyc_status,
        "tos_status": "approved" if bridge_customer else "pending",
        "rejection_reasons": None,
        "kyc_url": None,  # Not stored in current schema
        "tos_url": None,  # Not stored in current schema
    }


# ------------------ Front-end polling helper ------------------

@router.get("/link-status")
async def get_live_link_status(db: Session = Depends(get_db), jwt=Depends(get_current_user)):
    """Return live KYC link status straight from Bridge and persist any change."""
    user = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user has Bridge customer (indicates KYC completion)
    bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == user.id).first()
    
    if bridge_customer:
        return {
            "kyc_status": "approved",
            "tos_status": "approved",
            "tos_link": None,
            "rejection_reasons": [],
        }
    else:
        return {
            "kyc_status": "pending",
            "tos_status": "pending",
            "tos_link": None,
            "rejection_reasons": [],
        } 