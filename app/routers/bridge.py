from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Any, Dict

from app.dependencies.auth import get_current_user
from app.database import get_db
from app.services.bridge import BridgeClient

router = APIRouter(tags=["bridge"])

# -------------------------------
# Helpers
# -------------------------------

async def _ensure_bridge_customer(db: Session, user_identifier: str) -> str:
    """Return Bridge customer_id for the authenticated user. Auto-create if missing and KYC is active."""
    row = db.execute(
        text("""
        SELECT id, bridge_customer_id, kyc_status, first_name, last_name, email
        FROM users WHERE email = :id OR auth0_id = :id
        """),
        {"id": user_identifier},
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    user_id, cust_id, kyc_status, first_name, last_name, email = row

    if cust_id:
        return cust_id

    # Require successful KYC before creating Bridge customer
    if kyc_status not in ("approved", "active"):
        raise HTTPException(status_code=400, detail="KYC must be approved/active before creating Bridge customer")

    # Build minimal payload – more details can be attached later
    payload: Dict[str, Any] = {
        "type": "individual",
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
    }

    client = BridgeClient()
    try:
        resp = await client.create_customer(payload)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Bridge create_customer failed: {e}")

    cust_id = resp.get("id")
    if not cust_id:
        raise HTTPException(status_code=500, detail="Bridge did not return customer id")

    # Persist customer_id on user row
    db.execute(
        text("UPDATE users SET bridge_customer_id = :cid WHERE id = :uid"),
        {"cid": cust_id, "uid": user_id},
    )
    db.commit()
    # Auto-issue card if not already
    try:
        existing_card = db.execute(text("SELECT 1 FROM card_accounts WHERE user_id = :uid"),{"uid":user_id}).first()
        if not existing_card:
            card = await BridgeClient().create_card(cust_id,{"type":"virtual","currency":"usdb"})
            db.execute(text("INSERT INTO card_accounts (user_id, bridge_card_id, last4, state) VALUES (:u,:cid,:l4,:st)"),{"u":user_id,"cid":card.get('id'),"l4":card.get('last4'),"st":card.get('state')})
            db.commit()
    except Exception:
        pass
    return cust_id

# -------------------------------
# Endpoints
# -------------------------------

@router.get("/customers")
async def get_or_create_customer(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Return the authenticated user's Bridge customer record, creating it if missing."""
    cust_id = await _ensure_bridge_customer(db, current_user)
    client = BridgeClient()
    try:
        customer = await client.get_customer(cust_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Bridge get_customer failed: {e}")
    return customer

# -------- External Accounts --------

from pydantic import BaseModel, constr, Field

class ExternalAccountIn(BaseModel):
    currency: constr(strip_whitespace=True, to_lower=True)
    account_holder_name: str = Field(..., max_length=100)
    iban: str | None = None  # EU
    clabe: str | None = None  # Mexico
    account_number: str | None = None  # US account number
    routing_number: str | None = None  # US routing number

@router.post("/external_account")
async def create_external_account(
    body: ExternalAccountIn,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    cust_id = await _ensure_bridge_customer(db, current_user)
    client = BridgeClient()
    payload = body.dict(exclude_none=True)
    try:
        resp = await client.create_external_account(cust_id, payload)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Bridge create_external_account failed: {e}")
    return resp

# -------- Cards --------

class CardCreateIn(BaseModel):
    type: str = Field("virtual", description="Type of card to issue, e.g., virtual or physical")
    currency: str = Field("usdc", description="Currency for the card account")

@router.post("/cards")
async def create_card_account(
    body: CardCreateIn,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    cust_id = await _ensure_bridge_customer(db, current_user)
    client = BridgeClient()
    try:
        resp = await client.create_card(cust_id, body.dict())
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Bridge create_card failed: {e}")
    return resp

# -------- Plaid --------

@router.get("/plaid/link_request")
async def plaid_link_request(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    cust_id = await _ensure_bridge_customer(db, current_user)
    client = BridgeClient()
    try:
        resp = await client.plaid_link_request(cust_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Bridge plaid_link_request failed: {e}")
    return resp

@router.post("/plaid/exchange/{request_id}")
async def plaid_exchange_public_token(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    # Ensure customer exists (though not directly required for exchange step)
    await _ensure_bridge_customer(db, current_user)
    client = BridgeClient()
    try:
        resp = await client.plaid_exchange_token(request_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Bridge plaid_exchange_token failed: {e}")
    return resp 