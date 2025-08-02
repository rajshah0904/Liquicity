from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user
from ..models import User, BridgeCustomer
from ..bridge import BridgeClient
from typing import Optional

router = APIRouter(prefix="/virtual_accounts", tags=["virtual_accounts"])


@router.get("")
async def list_virtual_accounts(db: Session = Depends(get_db), jwt=Depends(get_current_user)):
    """Return all virtual accounts for the authenticated user."""
    user: Optional[User] = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get bridge customer from related table
    bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == user.id).first()
    if not bridge_customer:
        raise HTTPException(status_code=404, detail="Bridge customer not found")
    
    try:
        return BridgeClient().list_virtual_accounts(bridge_customer.id)
    except Exception as e:
        raise HTTPException(status_code=502, detail="Bridge unreachable") from e 