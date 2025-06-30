from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db, Base, engine
from ..models import User
from ..schemas import UserOut, TOSAcceptedIn, RegisterIn
import logging
from ..bridge import BridgeClient
from ..auth import get_current_user
from datetime import datetime
from fastapi_auth0.auth import Auth0User

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/onboard", tags=["onboard"])

_log = logging.getLogger(__name__)

@router.post("/register", response_model=UserOut)
def register(
    request: Request,
    payload: RegisterIn | None = None,
    auth_user: Auth0User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Prefer email from token, but fallback to body payload
    email = auth_user.email or (payload.email if payload else None)
    auth0_id = auth_user.id
    if not email:
        raise HTTPException(status_code=400, detail="email claim missing in token")

    user = db.query(User).filter(User.auth0_id == auth0_id).first()
    if not user:
        full_name = getattr(auth_user, 'name', '') or email.split('@')[0]

        user = User(
            email=email,
            auth0_id=auth0_id,
            full_name=full_name
        )
        db.add(user)
        db.flush()

        # Generate Bridge ToS link for brand-new user
        tos_url = BridgeClient().request_tos_links()["url"]
        user.tos_url = tos_url
        db.commit()

        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "tos_url": user.tos_url,
            "kyc_status": user.kyc_status,
        }

    # If the user already exists we shouldn't re-register – tell the client.
    raise HTTPException(status_code=409, detail="Account already exists")

@router.post("/tos/accepted")
async def tos_accepted(
    body: TOSAcceptedIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    # mark TOS link as accepted and return existing kyc_url
    user = db.query(User).filter(User.auth0_id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user ToS info
    user.tos_status = "approved"
    # signed_agreement_id no longer stored
    db.flush()

    # Create or refresh a KYC link now
    try:
        kyc_resp = BridgeClient().create_kyc_link({
            "type": "individual",
            "email": user.email,
            "endorsements": ["sepa"],
            # You may need to register this redirect URI in Bridge dashboard
            "redirect_uri": f"{request.url.scheme}://{request.url.hostname}:3000/kyc-verification"
        })
    except Exception as e:
        _log.error("create_kyc_link failed: %s", e)
        raise HTTPException(status_code=502, detail="Bridge create_kyc_link failed")

    user.kyc_link_id = kyc_resp.get("id")
    user.kyc_url = kyc_resp.get("kyc_link")
    user.tos_url = kyc_resp.get("tos_link") or user.tos_url
    db.commit()

    return {"kyc_url": user.kyc_url} 