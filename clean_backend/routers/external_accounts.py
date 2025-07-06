from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import requests
from typing import List, Dict

from ..database import get_db
from ..auth import get_current_user
from ..models import User, ExternalAccount
from ..bridge import BridgeClient

router = APIRouter(prefix="/external_accounts", tags=["external_accounts"])

class PublicTokenSchema(BaseModel):
    public_token: str

@router.get("/plaid/link_token")
def get_plaid_link_token(db: Session = Depends(get_db), jwt = Depends(get_current_user)):
    """Return a Plaid Link token for the authenticated user (US-only for now)."""
    user: User | None = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user or not user.bridge_customer_id:
        raise HTTPException(status_code=404, detail="Bridge customer id missing")

    try:
        resp = BridgeClient().get_plaid_link_token(user.bridge_customer_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail="Bridge unreachable") from e
    return resp

@router.post("/plaid/exchange/{link_token}")
def exchange_plaid_token(link_token: str, payload: PublicTokenSchema, db: Session = Depends(get_db), jwt = Depends(get_current_user)):
    """Exchange the Plaid public_token via Bridge."""
    # Ensure user exists (authorization)
    user: User | None = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        resp = BridgeClient().exchange_plaid_token(link_token, payload.public_token)
    except requests.HTTPError as e:
        # Forward Bridge's error response directly for easier debugging
        status = e.response.status_code if e.response else 502
        detail = e.response.text if e.response else str(e)
        raise HTTPException(status_code=status, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=502, detail="Bridge unreachable") from e
    return resp

# -------- List accounts --------

@router.get("/accounts")
def list_external_accounts(db: Session = Depends(get_db), jwt = Depends(get_current_user)):
    """Return all Bridge external accounts for the authenticated user."""
    user: User | None = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user or not user.bridge_customer_id:
        raise HTTPException(status_code=404, detail="Bridge customer id missing")

    try:
        bridge_resp = BridgeClient().list_external_accounts(user.bridge_customer_id)
        accounts = bridge_resp.get("data", [])
    except Exception as e:
        raise HTTPException(status_code=502, detail="Bridge unreachable") from e

    mapped_accounts = _upsert_accounts(db, user, accounts)
    return {"accounts": mapped_accounts}

# -------- Sync accounts (noop for now) --------

@router.post("/sync")
def sync_accounts(db: Session = Depends(get_db), jwt = Depends(get_current_user)):
    """Trigger a sync – currently just fetches latest accounts from Bridge and returns count."""
    user: User | None = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user or not user.bridge_customer_id:
        raise HTTPException(status_code=404, detail="Bridge customer id missing")

    try:
        bridge_resp = BridgeClient().list_external_accounts(user.bridge_customer_id)
        accounts = bridge_resp.get("data", [])
    except Exception as e:
        raise HTTPException(status_code=502, detail="Bridge unreachable") from e

    _upsert_accounts(db, user, accounts)
    return {"updated": len(accounts)}

# Helper to upsert Bridge account list into DB and return simplified list
def _upsert_accounts(db: Session, user: User, accounts: List[Dict]):
    mapped = []
    for acc in accounts:
        bank_name = acc.get("bank_name") or acc.get("name")
        last4 = (
            acc.get("account", {}).get("last_4")
            or acc.get("account", {}).get("last4")
            or acc.get("last_4")
            or acc.get("last4")
        )
        currency = acc.get("currency")
        status = acc.get("status")

        ext = db.query(ExternalAccount).filter(ExternalAccount.id == acc["id"]).first()
        if not ext:
            ext = ExternalAccount(id=acc["id"], user_id=user.id)
            db.add(ext)
        ext.bank_name = bank_name
        ext.last4 = last4
        ext.currency = currency
        ext.status = status

        mapped.append({
            "id": acc["id"],
            "bank_name": bank_name,
            "name": bank_name,
            "last4": last4,
            "accountNumber": f"****{last4}" if last4 else None,
            "currency": currency,
            "status": status,
        })
    db.commit()
    return mapped 

@router.post("/accounts")
def create_external_account(payload: Dict, db: Session = Depends(get_db), jwt = Depends(get_current_user)):
    """Create a new external account for the authenticated user via Bridge and persist basic metadata locally.

    The payload is passed through to Bridge's POST /customers/{customer_id}/external_accounts endpoint.
    """
    user: User | None = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user or not user.bridge_customer_id:
        raise HTTPException(status_code=404, detail="Bridge customer id missing")

    try:
        bridge_resp = BridgeClient().create_external_account(user.bridge_customer_id, payload)
    except requests.HTTPError as e:
        status = e.response.status_code if e.response else 502
        detail = e.response.text if e.response else str(e)
        raise HTTPException(status_code=status, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=502, detail="Bridge unreachable") from e

    # Upsert the newly created account into local DB
    acc_id = bridge_resp.get("id")
    if acc_id:
        ext = db.query(ExternalAccount).filter(ExternalAccount.id == acc_id).first()
        if not ext:
            ext = ExternalAccount(id=acc_id, user_id=user.id)
            db.add(ext)
        # Update display fields
        ext.bank_name = bridge_resp.get("bank_name") or payload.get("bank_name")
        # Attempt to find last4 digits in common locations
        last4 = (
            bridge_resp.get("account", {}).get("last_4")
            or bridge_resp.get("account", {}).get("last4")
            or bridge_resp.get("last_4")
            or bridge_resp.get("last4")
        )
        ext.last4 = last4
        ext.currency = bridge_resp.get("currency") or payload.get("currency")
        ext.status = bridge_resp.get("status")
        db.commit()

    return bridge_resp 

@router.get("/accounts/{account_id}")
def get_external_account_details(account_id: str, db: Session = Depends(get_db), jwt = Depends(get_current_user)):
    """Return details for a single external account belonging to the authenticated user.

    This is a thin wrapper around Bridge's GET /customers/{customer_id}/external_accounts/{id}
    (falling back to /external_accounts/{id}). We also upsert the latest metadata into
    the local `external_accounts_v2` table so cached lists stay in sync.
    """
    # Authorize user
    user: User | None = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user or not user.bridge_customer_id:
        raise HTTPException(status_code=404, detail="Bridge customer id missing")

    try:
        bridge_resp = BridgeClient().get_external_account(account_id, user.bridge_customer_id)
    except requests.HTTPError as e:
        status = e.response.status_code if e.response else 502
        detail = e.response.text if e.response else str(e)
        raise HTTPException(status_code=status, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=502, detail="Bridge unreachable") from e

    # Upsert into DB for caching/display purposes
    bank_name = bridge_resp.get("bank_name") or bridge_resp.get("name")
    last4 = (
        bridge_resp.get("account", {}).get("last_4")
        or bridge_resp.get("account", {}).get("last4")
        or bridge_resp.get("last_4")
        or bridge_resp.get("last4")
    )
    currency = bridge_resp.get("currency")
    status = bridge_resp.get("status")

    ext = db.query(ExternalAccount).filter(ExternalAccount.id == account_id).first()
    if not ext:
        ext = ExternalAccount(id=account_id, user_id=user.id)
        db.add(ext)
    ext.bank_name = bank_name
    ext.last4 = last4
    ext.currency = currency
    ext.status = status
    db.commit()

    return {
        "id": account_id,
        "bank_name": bank_name,
        "name": bank_name,
        "last4": last4,
        "accountNumber": f"****{last4}" if last4 else None,
        "currency": currency,
        "status": status,
        "raw": bridge_resp,  # Expose full Bridge response for frontend flexibility
    } 