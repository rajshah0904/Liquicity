from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, condecimal
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.utils.notify import add_notification
from typing import List

router = APIRouter(prefix="/requests", tags=["requests"])

class RequestIn(BaseModel):
    amount: condecimal(gt=Decimal("0"), max_digits=18, decimal_places=2)
    note: str | None = None

@router.post("")
async def create_request(body: RequestIn, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    # get requester id
    row = db.execute(text("SELECT id FROM users WHERE email = :id OR auth0_id = :id"),{"id":current_user}).first()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    requester_id = row[0]
    res = db.execute(text("""INSERT INTO money_requests (requester_id,amount,note) VALUES (:r,:a,:n) RETURNING id"""),{"r":requester_id,"a":body.amount,"n":body.note}).first()
    db.commit()
    # Notify self
    add_notification(db, requester_id, 'request', f'You requested {body.amount} from others')
    return {"success":True, "request_id": res[0]}

@router.get("")
async def list_requests(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    row = db.execute(text("SELECT id FROM users WHERE email = :id OR auth0_id = :id"),{"id":current_user}).first()
    if not row:
        return {"requests": []}
    uid = row[0]
    rs = db.execute(text("SELECT id, requester_id, amount, note, status, created_at FROM money_requests WHERE requester_id = :u OR id IN (SELECT id FROM money_requests WHERE status='pending') ORDER BY id DESC"),{"u":uid}).fetchall()
    return {"requests":[{"id":r[0],"requester_id":r[1],"amount":str(r[2]),"note":r[3],"status":r[4],"created_at":r[5]} for r in rs]} 