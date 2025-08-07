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
    # DEBUG: Log the Auth0 user info and payload
    _log.info(f"register called with Auth0 user: id={auth_user.id}, email={auth_user.email}")
    _log.info(f"register payload: {payload}")
    
    # Prefer email from token, but fallback to body payload
    email = auth_user.email or (payload.email if payload else None)
    auth0_id = auth_user.id
    
    _log.info(f"Final email resolved: {email} (from token: {auth_user.email}, from payload: {payload.email if payload else 'No payload'})")
    
    if not email:
        _log.error(f"REGISTRATION_FAILED: No email available - Auth0_token_email={auth_user.email}, payload_email={payload.email if payload else 'No payload'}")
        raise HTTPException(status_code=400, detail="email claim missing in token")

    user = db.query(User).filter(User.auth0_id == auth0_id).first()
    if not user:
        _log.info(f"Creating new user: email={email}, auth0_id={auth0_id}")
        user = User(
            email=email,
            auth0_id=auth0_id
        )
        db.add(user)
        db.commit()

        _log.info(f"Successfully created user: {user.id}")
        return {
            "id": str(user.id),
            "email": user.email,
        }

    # If the user already exists we shouldn't re-register – tell the client.
    _log.warning(f"User already exists: {user.email} (ID: {user.id})")
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