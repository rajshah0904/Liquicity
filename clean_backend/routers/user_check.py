from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, BridgeUser
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

    # Determine next onboarding step
    # 1. Country not yet chosen
    if not db_user.country:
        return {
            "exists": True,
            "next_step": "country",
            "kyc_complete": False,
        }

    # 2. TOS not yet approved
    if db_user.tos_status != "approved":
        return {
            "exists": True,
            "next_step": "tos",
            "tos_url": db_user.tos_url,
            "kyc_complete": False,
        }

    # 3. KYC in progress / pending
    if db_user.kyc_status != "approved":
        return {
            "exists": True,
            "next_step": "kyc",
            "kyc_url": db_user.kyc_url,
            "kyc_complete": False,
        }

    # -----------------------------------------------
    # Edge-case recovery: KYC approved but no customer
    # -----------------------------------------------
    if db_user.bridge_customer_id is None and db_user.kyc_status == "approved":
        # We need signed_agreement_id (if present) to create the customer
        payload = {
            "type": "individual",
            "email": db_user.email,
        }
        try:
            customer = BridgeClient().create_customer(payload)
            db_user.bridge_customer_id = customer.get("id")

            # Upsert BridgeUser row (customer only at this stage)
            bridge_rec = db.query(BridgeUser).filter(BridgeUser.user_id == db_user.id).first()
            if not bridge_rec:
                db.add(
                    BridgeUser(
                        user_id=db_user.id,
                        bridge_customer_id=db_user.bridge_customer_id,
                    )
                )
            else:
                bridge_rec.bridge_customer_id = db_user.bridge_customer_id
            db.commit()
        except Exception as e:
            # Log; we'll retry on next login
            import logging
            logging.getLogger(__name__).error("create_customer failed during user_check: %s", e)

    # Create wallet if user is fully onboarded but wallet missing
    if (
        db_user.bridge_wallet_id is None
        and db_user.bridge_customer_id is not None
        and db_user.kyc_status == "approved"
        and db_user.tos_status == "approved"
    ):
        try:
            wallet = BridgeClient().create_wallet(db_user.bridge_customer_id, chain="solana")
            db_user.bridge_wallet_id = wallet.get("id")

            # Upsert BridgeUser entry
            bridge_rec = db.query(BridgeUser).filter(BridgeUser.user_id == db_user.id).first()
            if not bridge_rec:
                bridge_rec = BridgeUser(
                    user_id=db_user.id,
                    bridge_customer_id=db_user.bridge_customer_id,
                    bridge_wallet_id=db_user.bridge_wallet_id,
                )
                db.add(bridge_rec)
            else:
                bridge_rec.bridge_customer_id = db_user.bridge_customer_id
                bridge_rec.bridge_wallet_id = db_user.bridge_wallet_id
            db.commit()
        except Exception as e:
            # Not critical for user check – log and continue
            import logging
            logging.getLogger(__name__).error("create_wallet failed during user_check: %s", e)

    # Create virtual account if missing
    if (
        db_user.bridge_wallet_id is not None
        and db_user.bridge_customer_id is not None
        and db_user.kyc_status == "approved"
        and db_user.tos_status == "approved"
    ):
        bridge_rec = db.query(BridgeUser).filter(BridgeUser.user_id == db_user.id).first()
        if bridge_rec and bridge_rec.virtual_account_id is None:
            try:
                wallet_address = None
                # fetch wallet for address
                wallet_resp = BridgeClient().get_wallet(db_user.bridge_customer_id, db_user.bridge_wallet_id)
                wallet_address = wallet_resp.get("address")
                va_resp = BridgeClient().get_or_create_usd_virtual_account(db_user.bridge_customer_id, wallet_address)
                bridge_rec.virtual_account_id = va_resp.get("id")
                db.commit()
            except Exception as e:
                import logging
                logging.getLogger(__name__).error("create_virtual_account failed during user_check: %s", e)

    # 4. Fully onboarded
    return {
        "exists": True,
        "next_step": "done",
        "kyc_complete": True,
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