from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user
from ..models import User
from ..bridge import BridgeClient

router = APIRouter(prefix="/virtual_accounts", tags=["virtual_accounts"])


@router.get("")
async def list_virtual_accounts(db: Session = Depends(get_db), jwt=Depends(get_current_user)):
    """Return all virtual accounts for the authenticated user."""
    user: User | None = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user or not user.bridge_customer_id:
        raise HTTPException(status_code=404, detail="Bridge customer id missing")
    try:
        return BridgeClient().list_virtual_accounts(user.bridge_customer_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail="Bridge unreachable") from e 