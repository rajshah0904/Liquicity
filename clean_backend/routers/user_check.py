from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, BridgeCustomer, BridgeWallet
from ..auth import get_current_user
from fastapi_auth0.auth import Auth0User
from sqlalchemy import func
from ..bridge import BridgeClient

router = APIRouter(tags=["auth"])


def _user_by_sub(db: Session, sub: str):
    return db.query(User).filter((User.auth0_id == sub) | (User.email == sub)).first()


@router.get("/user/check")
async def user_check(db: Session = Depends(get_db), auth_user: Auth0User = Depends(get_current_user)):
    """Return whether a record exists for the current Auth0 user and if KYC is complete."""
    db_user = _user_by_sub(db, auth_user.id)
    exists = bool(db_user)
    if not exists:
        return {"exists": False, "next_step": "register"}

    # Check if user has completed each step of onboarding
    bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == db_user.id).first()
    bridge_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == db_user.id).first()
    
    # Determine next step based on what's completed
    if not bridge_customer:
        # User exists but no Bridge customer - needs country selection and TOS
        return {
            "exists": True,
            "next_step": "country",
        }
    elif not bridge_wallet:
        # Has customer but no wallet - needs KYC
        return {
            "exists": True,
            "next_step": "kyc",
        }
    else:
        # Has both customer and wallet - onboarding complete
        return {
            "exists": True,
            "next_step": "done",
        }


@router.options("/user/check", include_in_schema=False)
async def options_user_check() -> Response:
    """CORS pre-flight helper for /user/check."""
    return Response(status_code=200)


@router.get("/user/email-exists")
async def email_exists(email: str, db: Session = Depends(get_db)):
    """Public endpoint to check whether an account already exists for the given email address."""
    exists = bool(db.query(User).filter(func.lower(User.email) == email.lower()).first())
    return {"exists": exists} 