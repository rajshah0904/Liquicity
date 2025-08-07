from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, BridgeCustomer, BridgeWallet
from ..auth import get_current_user
from fastapi_auth0.auth import Auth0User
from sqlalchemy import func
from ..bridge import BridgeClient
import logging
import datetime

router = APIRouter(tags=["auth"])
_log = logging.getLogger(__name__)


def _user_by_sub(db: Session, sub: str):
    """Look up user by Auth0 subject ID only - NEVER by email to prevent auth bugs"""
    return db.query(User).filter(User.auth0_id == sub).first()


@router.get("/user/check")
async def user_check(db: Session = Depends(get_db), auth_user: Auth0User = Depends(get_current_user)):
    """Return comprehensive user onboarding state for proper flow resumption."""
    
    # DEBUG: Log the Auth0 user info
    _log.info(f"user_check called with Auth0 user: id={auth_user.id}, email={auth_user.email}")
    
    db_user = _user_by_sub(db, auth_user.id)
    
    if not db_user:
        _log.info(f"No user found for Auth0 ID: {auth_user.id}")
        return {"exists": False, "next_step": "register"}
    
    _log.info(f"Found existing user: {db_user.email} (ID: {db_user.id})")
    
    # Get related onboarding data
    bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == db_user.id).first()
    bridge_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == db_user.id).first()
    
    # Determine current onboarding state and next step
    if not bridge_customer:
        # No Bridge customer means KYC hasn't been completed yet
        # PRODUCTION: Only auth details stored before KYC completion
        return {
            "exists": True,
            "next_step": "kyc",
            "user_id": str(db_user.id),
            "email": db_user.email,
            "completed_steps": ["register"]
        }
    elif bridge_customer and not bridge_wallet:
        # Has customer but no wallet - KYC completed but wallet creation failed
        # Try to create wallet automatically
        _log.info(f"User {db_user.id} has Bridge customer but no wallet - will create wallet")
        return {
            "exists": True,
            "next_step": "create_wallet",
            "user_id": str(db_user.id),
            "email": db_user.email,
            "region": db_user.region,
            "bridge_customer_id": bridge_customer.id,
            "completed_steps": ["register", "region", "kyc"]
        }
    else:
        # Has both customer and wallet - onboarding complete
        return {
            "exists": True,
            "next_step": "done",
            "user_id": str(db_user.id),
            "email": db_user.email,
            "region": db_user.region,
            "bridge_customer_id": bridge_customer.id,
            "bridge_wallet_id": bridge_wallet.wallet_id,
            "fiat_currency": bridge_wallet.fiat_currency,
            "completed_steps": ["register", "region", "kyc", "wallet"]
        }


@router.options("/user/check", include_in_schema=False)
async def options_user_check() -> Response:
    """CORS pre-flight helper for /user/check."""
    return Response(status_code=200)


@router.post("/user/create-wallet")
async def create_wallet_if_approved(db: Session = Depends(get_db), auth_user: Auth0User = Depends(get_current_user)):
    """Create wallet automatically if user has approved KYC but no wallet exists."""
    from ..utils.currency_utils import get_fiat_currency_from_region
    
    db_user = _user_by_sub(db, auth_user.id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == db_user.id).first()
    if not bridge_customer:
        raise HTTPException(status_code=400, detail="Bridge customer not found")
    
    bridge_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == db_user.id).first()
    if bridge_wallet:
        # Wallet already exists
        return {
            "wallet_created": False,
            "message": "Wallet already exists",
            "wallet_id": bridge_wallet.wallet_id
        }
    
    try:
        # Check KYC status
        customer_data = BridgeClient().get_customer(bridge_customer.id)
        if customer_data.get("status") != "approved":
            raise HTTPException(status_code=400, detail=f"KYC not approved. Status: {customer_data.get('status')}")
        
        # Create wallet
        wallet = BridgeClient().create_wallet(bridge_customer.id, chain="solana")
        
        # Create BridgeWallet record with fiat currency mapping
        fiat_currency = get_fiat_currency_from_region(db_user.region) if db_user.region else 'USD'
        
        bridge_wallet = BridgeWallet(
            wallet_id=wallet.get("id"),
            user_id=db_user.id,
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
        db.commit()
        
        _log.info(f"Created Bridge wallet {bridge_wallet.wallet_id} for user {db_user.id}")
        
        return {
            "wallet_created": True,
            "wallet_id": bridge_wallet.wallet_id,
            "fiat_currency": fiat_currency,
            "message": "Wallet created successfully"
        }
        
    except Exception as e:
        _log.error(f"Failed to create wallet for user {db_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create wallet")


@router.get("/user/email-exists")
async def email_exists(email: str, db: Session = Depends(get_db)):
    """Public endpoint to check whether an account already exists for the given email address."""
    exists = bool(db.query(User).filter(func.lower(User.email) == email.lower()).first())
    return {"exists": exists} 