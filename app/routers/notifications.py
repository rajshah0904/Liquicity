from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("")
async def get_notifications(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    rows = db.execute(text("SELECT id FROM users WHERE email = :id OR auth0_id = :id"),{"id":current_user}).first()
    if not rows:
        return {"notifications": []}
    user_id = rows[0]
    rs = db.execute(text("SELECT id, type, message, created_at FROM notifications WHERE user_id = :u ORDER BY id DESC LIMIT 100"),{"u":user_id}).fetchall()
    return {"notifications":[{"id":r[0],"type":r[1],"message":r[2],"created_at":r[3]} for r in rs]} 