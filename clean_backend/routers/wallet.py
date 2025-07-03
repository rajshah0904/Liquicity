from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user
from ..models import User
from ..bridge import BridgeClient

router = APIRouter(prefix="/wallet", tags=["wallet"])

@router.get("")
async def get_bridge_wallet(db: Session = Depends(get_db), jwt=Depends(get_current_user)):
    user = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user or not user.bridge_customer_id or not user.bridge_wallet_id:
        raise HTTPException(status_code=404, detail="Wallet not found")
    try:
        wallet = BridgeClient().get_wallet(user.bridge_customer_id, user.bridge_wallet_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail="Bridge unreachable") from e
    return wallet

@router.get("/history")
async def wallet_history(db: Session = Depends(get_db), jwt=Depends(get_current_user)):
    user = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user or not user.bridge_wallet_id:
        raise HTTPException(status_code=404, detail="Wallet not found")
    try:
        history = BridgeClient().get_wallet_history(user.bridge_wallet_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail="Bridge unreachable") from e
    return history 