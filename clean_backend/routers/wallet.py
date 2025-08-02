from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user
from ..models import User, BridgeCustomer, BridgeWallet
from ..bridge import BridgeClient

router = APIRouter(prefix="/wallet", tags=["wallet"])

@router.get("")
async def get_bridge_wallet(db: Session = Depends(get_db), jwt=Depends(get_current_user)):
    user = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get bridge customer and wallet from related tables
    bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == user.id).first()
    if not bridge_customer:
        raise HTTPException(status_code=404, detail="Bridge customer not found")
    
    bridge_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == user.id).first()
    if not bridge_wallet:
        raise HTTPException(status_code=404, detail="Bridge wallet not found")
    
    try:
        wallet = BridgeClient().get_wallet(bridge_customer.id, bridge_wallet.id)
    except Exception as e:
        raise HTTPException(status_code=502, detail="Bridge unreachable") from e
    return wallet

@router.get("/history")
async def wallet_history(db: Session = Depends(get_db), jwt=Depends(get_current_user)):
    user = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    bridge_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == user.id).first()
    if not bridge_wallet:
        raise HTTPException(status_code=404, detail="Bridge wallet not found")
    
    try:
        history = BridgeClient().get_wallet_history(bridge_wallet.id)
    except Exception as e:
        raise HTTPException(status_code=502, detail="Bridge unreachable") from e
    return history 