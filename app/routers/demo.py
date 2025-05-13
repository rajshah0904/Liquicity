from fastapi import APIRouter, Depends, HTTPException
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
import os
from app.services.bridge import DEMO_MODE, _DemoBridgeClient
import uuid
from app.routers.transfer import send_money as real_send_money, SendIn
from app.routers.wallet import wallet_overview

router = APIRouter(prefix="/demo", tags=["demo"], include_in_schema=False)

if DEMO_MODE:
    @router.post("/topup")
    async def demo_topup(user_identifier: str, amount: Decimal, db: Session = Depends(get_db)):
        """Credit `amount` into the user's demo Polygon wallet. user_identifier can be email or auth0_id."""
        row = db.execute(text("SELECT bridge_customer_id FROM users WHERE email = :id OR auth0_id = :id"), {"id": user_identifier}).first()
        if not row or not row[0]:
            raise HTTPException(status_code=404, detail="User not found or no Bridge customer id")
        cust_id = row[0]
        demo = _DemoBridgeClient()
        wallet = demo._ensure_wallet(cust_id)
        with db.begin():
            db.execute(text("UPDATE demo_wallets SET balance = balance + :amt WHERE wallet_id = :wid"), {"amt": amount, "wid": wallet['id']})
        return {"wallet_id": wallet['id'], "new_balance": str(Decimal(wallet['balance']) + amount)}

    @router.post("/create_user")
    async def demo_create_user(email: str, country: str, db: Session = Depends(get_db)):
        """Create a demo Auth0-style user row with given country & auto Bridge customer id."""
        existing = db.execute(text("SELECT id FROM users WHERE email = :e"), {"e": email}).first()
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")
        user_id_row = db.execute(text("""
            INSERT INTO users (email, first_name, last_name, country, account_type) VALUES (:e, :f, :l, :c, 'auth0') RETURNING id
        """), {"e": email, "f": email.split('@')[0].title(), "l": "Demo", "c": country.upper()}).first()
        db.commit()
        user_id = user_id_row[0]
        # create Bridge customer id
        cust_id = f"demo_cust_{uuid.uuid4().hex[:8]}"
        db.execute(text("UPDATE users SET bridge_customer_id = :cid WHERE id = :uid"), {"cid": cust_id, "uid": user_id})
        db.commit()
        return {"user_id": user_id, "customer_id": cust_id}

    @router.post("/send")
    async def demo_send(body: SendIn, sender_identifier: str, db: Session = Depends(get_db)):
        """Perform a send as `sender_identifier` bypassing Auth0 auth."""
        # monkey patch depends by passing sender identifier
        return await real_send_money(body=body, db=db, current_user=sender_identifier)

    @router.get("/wallet")
    async def demo_wallet(identifier: str, db: Session = Depends(get_db)):
        return await wallet_overview(db=db, current_user=identifier) 