from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, BridgeUser
from ..bridge import BridgeClient
from ..auth import get_current_user
import logging
import json
import datetime

router = APIRouter(prefix="/kyc", tags=["kyc"])
_log = logging.getLogger(__name__)


def _lookup_user(db: Session, sub: str) -> User | None:
    return db.query(User).filter((User.auth0_id == sub) | (User.email == sub)).first()


@router.post("/link")
async def generate_kyc_link(db: Session = Depends(get_db), jwt: dict = Depends(get_current_user)):
    user = _lookup_user(db, jwt.get("sub"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.email:
        raise HTTPException(status_code=400, detail="Email required for KYC link generation")

    link = BridgeClient().create_kyc_link({
        "type": "individual",
        "email": user.email,
        "endorsements": ["sepa"],
    })

    # Save link details to user
    user.kyc_link_id = link.get("id")
    user.kyc_url = link.get("kyc_link")
    user.tos_url = link.get("tos_link") or user.tos_url
    db.commit()
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

    # Find user by bridge customer id or kyc_link_id
    user = None
    if cid:
        user = db.query(User).filter(User.bridge_customer_id == cid).first()
    if not user and kyc_link_id:
        user = db.query(User).filter(User.kyc_link_id == kyc_link_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.kyc_status = status
    # Persist additional details on user
    if tos_status:
        user.tos_status = tos_status
    if rejection_reasons is not None:
        user.rejection_reasons = json.dumps(rejection_reasons) if isinstance(rejection_reasons, list) else str(rejection_reasons)

    if status == "approved":
        # When approved create wallet
        if not user.bridge_customer_id:
            signed_agreement_id = None  # no longer stored locally
            payload = {
                "type": "individual",
                "email": user.email,
            }
            if signed_agreement_id:
                payload["signed_agreement_id"] = signed_agreement_id
            try:
                customer = BridgeClient().create_customer(payload)
                user.bridge_customer_id = customer.get("id")
                user.kyc_status = customer.get("status", status)

                # Upsert BridgeUser with customer id (wallet may be null yet)
                bridge_rec = db.query(BridgeUser).filter(BridgeUser.user_id == user.id).first()
                if not bridge_rec:
                    bridge_rec = BridgeUser(
                        user_id=user.id,
                        bridge_customer_id=user.bridge_customer_id,
                    )
                    db.add(bridge_rec)
                else:
                    bridge_rec.bridge_customer_id = user.bridge_customer_id
            except Exception as e:
                _log.error("create_customer failed: %s", e)
        else:
            user.kyc_status = status

        # ---------------- Wallet creation ----------------
        try:
            # Ensure ToS approved before creating wallet & virtual account
            if user.tos_status == "approved" and not user.bridge_wallet_id and user.bridge_customer_id and user.kyc_status == "approved":
                wallet = BridgeClient().create_wallet(user.bridge_customer_id, chain="solana")
                user.bridge_wallet_id = wallet.get("id")
                _log.info("Bridge wallet %s created for user %s", user.bridge_wallet_id, user.id)

                # Upsert BridgeUser record
                bridge_rec = db.query(BridgeUser).filter(BridgeUser.user_id == user.id).first()
                if not bridge_rec:
                    bridge_rec = BridgeUser(user_id=user.id)
                    db.add(bridge_rec)

                    bridge_rec.bridge_customer_id = user.bridge_customer_id
                    bridge_rec.bridge_wallet_id = user.bridge_wallet_id

                # Create a default virtual account once per user
                if not bridge_rec.virtual_account_id:
                    try:
                        va_resp = BridgeClient().get_or_create_usd_virtual_account(
                            user.bridge_customer_id,
                            wallet.get("address"),
                        )
                        bridge_rec.virtual_account_id = va_resp.get("id")
                        _log.info("Virtual account %s created for user %s", bridge_rec.virtual_account_id, user.id)
                    except Exception as e:
                        _log.error("create_virtual_account failed: %s", e)
        except Exception as e:
            # Non-fatal – log and continue; wallet creation can be retried later
            _log.error("create_wallet or related steps failed: %s", e)
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
    return {
        "kyc_status": user.kyc_status,
        "link_status": user.kyc_status,
        "tos_status": user.tos_status,
        "rejection_reasons": json.loads(user.rejection_reasons) if user.rejection_reasons else None,
        "kyc_url": user.kyc_url,
        "tos_url": user.tos_url,
    }


# ------------------ Front-end polling helper ------------------

@router.get("/link-status")
async def get_live_link_status(db: Session = Depends(get_db), jwt=Depends(get_current_user)):
    """Return live KYC link status straight from Bridge and persist any change."""
    user = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.kyc_link_id:
        raise HTTPException(status_code=404, detail="No KYC link for user")

    try:
        live = BridgeClient().get_kyc_link(user.kyc_link_id)
    except Exception as e:
        _log.error("Bridge get_kyc_link failed: %s", e)
        raise HTTPException(status_code=502, detail="Bridge unreachable")

    # Update user fields from live response
    if live.get("kyc_status"):
        user.kyc_status = live["kyc_status"]
    if live.get("tos_status"):
        user.tos_status = live["tos_status"]
    if live.get("id"):
        user.kyc_link_id = live["id"]
    if live.get("full_name"):
        user.full_name = live["full_name"]
    if live.get("type"):
        user.kyc_type = live["type"]
    if live.get("kyc_link"):
        user.kyc_url = live["kyc_link"]
    if live.get("tos_link"):
        user.tos_url = live["tos_link"]
    db.commit()

    return {
        "kyc_status": user.kyc_status,
        "tos_status": user.tos_status,
        "tos_link": user.tos_url,
        "rejection_reasons": live.get("rejection_reasons", []),
    } 