from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db, Base, engine
from ..models import User
from ..schemas import UserOut, TOSAcceptedIn, RegisterIn
import logging
from ..bridge import BridgeClient
from ..auth import get_current_user
from datetime import datetime
from fastapi_auth0.auth import Auth0User

router = APIRouter(prefix="/onboard", tags=["onboard"])

_log = logging.getLogger(__name__)

@router.post("/register", response_model=UserOut)
def register(
    request: Request,
    payload: Optional[RegisterIn] = None,
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
        user = User(
            email=email,
            auth0_id=auth0_id
        )
        db.add(user)
        db.commit()

        return {
            "id": str(user.id),
            "email": user.email,
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
    # mark TOS link as accepted and return KYC link
    user = db.query(User).filter(User.auth0_id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

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

    return {"kyc_url": kyc_resp.get("kyc_link")} 