from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import requests
from typing import List, Dict

from ..database import get_db
from ..auth import get_current_user
from ..models import User, ExternalAccount
from ..bridge import BridgeClient
from ..services.plaid_client import PlaidClient
from ..models.plaid import PlaidItem

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
    # ------------------------------------------------------------------
    # Plaid integration – exchange public_token for access_token and store
    # ------------------------------------------------------------------
    access_token = None
    item_id = None
    try:
        plaid_resp = PlaidClient().exchange_public_token(payload.public_token)
        access_token = plaid_resp.get("access_token")
        item_id = plaid_resp.get("item_id")
    except Exception as e:
        # Log but don't fail the whole request – the Bridge exchange already succeeded
        import logging
        logging.getLogger(__name__).warning("Plaid exchange failed: %s", e)

    # ------------------------------------------------------------------
    # Identity verification – ensure bank account owner matches user name
    # ------------------------------------------------------------------
    if access_token and user.full_name:
        try:
            ident = PlaidClient().get_identity(access_token)
            owner_names: set[str] = set()
            for acct in ident.get("accounts", []):
                for owner in acct.get("owners", []):
                    owner_names.update(n.lower() for n in owner.get("names", []))

            user_name = user.full_name.lower()

            # Simple containment / exact match check; can be replaced with fuzzy logic
            match_found = any(user_name in n or n in user_name for n in owner_names)
            if not match_found:
                raise HTTPException(
                    status_code=400,
                    detail="Bank account owner name does not match registered user",
                )
        except HTTPException:
            raise  # propagate mismatch
        except Exception as e:
            # Non-blocking – just log if Plaid Identity call fails
            import logging
            logging.getLogger(__name__).warning("Plaid identity check failed: %s", e)

    external_account_id = resp.get("external_account_id") or resp.get("id")
    if external_account_id and access_token:
        item = db.query(PlaidItem).filter(PlaidItem.external_account_id == external_account_id).first()
        if not item:
            item = PlaidItem(
                external_account_id=external_account_id,
                access_token=access_token,
                item_id=item_id,
            )
            db.add(item)
        else:
            item.access_token = access_token
            item.item_id = item_id
        db.commit()

    if item_id:
        resp["plaid_item_id"] = item_id
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

# ---------------------------------------------------------------------------
# Plaid passthrough endpoints (Balance / Auth / Identity)
# ---------------------------------------------------------------------------

@router.get("/accounts/{account_id}/balance")
def get_account_balance(account_id: str, db: Session = Depends(get_db), jwt = Depends(get_current_user)):
    """Fetch real-time balance for the specified external account via Plaid."""
    user: User | None = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify ownership of the external account
    ext = (
        db.query(ExternalAccount)
        .filter(ExternalAccount.id == account_id, ExternalAccount.user_id == user.id)
        .first()
    )
    if not ext:
        raise HTTPException(status_code=404, detail="Account not found")

    item = db.query(PlaidItem).filter(PlaidItem.external_account_id == account_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Plaid token not found")

    try:
        return PlaidClient().get_balance(item.access_token)
    except requests.HTTPError as e:
        status = e.response.status_code if e.response else 502
        detail = e.response.text if e.response else str(e)
        raise HTTPException(status_code=status, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=502, detail="Plaid unreachable") from e


@router.get("/accounts/{account_id}/auth")
def get_account_auth(account_id: str, db: Session = Depends(get_db), jwt = Depends(get_current_user)):
    """Retrieve ACH account/routing numbers via Plaid Auth."""
    user: User | None = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ext = db.query(ExternalAccount).filter(ExternalAccount.id == account_id, ExternalAccount.user_id == user.id).first()
    if not ext:
        raise HTTPException(status_code=404, detail="Account not found")

    item = db.query(PlaidItem).filter(PlaidItem.external_account_id == account_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Plaid token not found")

    try:
        return PlaidClient().get_auth(item.access_token)
    except requests.HTTPError as e:
        status = e.response.status_code if e.response else 502
        detail = e.response.text if e.response else str(e)
        raise HTTPException(status_code=status, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=502, detail="Plaid unreachable") from e


@router.get("/accounts/{account_id}/identity")
def get_account_identity(account_id: str, db: Session = Depends(get_db), jwt = Depends(get_current_user)):
    """Return user identity information (name / address) from Plaid."""
    user: User | None = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ext = db.query(ExternalAccount).filter(ExternalAccount.id == account_id, ExternalAccount.user_id == user.id).first()
    if not ext:
        raise HTTPException(status_code=404, detail="Account not found")

    item = db.query(PlaidItem).filter(PlaidItem.external_account_id == account_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Plaid token not found")

    try:
        return PlaidClient().get_identity(item.access_token)
    except requests.HTTPError as e:
        status = e.response.status_code if e.response else 502
        detail = e.response.text if e.response else str(e)
        raise HTTPException(status_code=status, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=502, detail="Plaid unreachable") from e

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

# ---------------------------------------------------------------------------
# Delete external account                                                    
# ---------------------------------------------------------------------------

@router.delete("/accounts/{account_id}")
def delete_external_account(account_id: str, db: Session = Depends(get_db), jwt = Depends(get_current_user)):
    """Delete an external account both on Bridge and locally."""
    user: User | None = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user or not user.bridge_customer_id:
        raise HTTPException(status_code=404, detail="Bridge customer id missing")

    # Verify ownership locally first
    ext = db.query(ExternalAccount).filter(ExternalAccount.id == account_id, ExternalAccount.user_id == user.id).first()
    if not ext:
        raise HTTPException(status_code=404, detail="Account not found")

    try:
        BridgeClient().delete_external_account(user.bridge_customer_id, account_id)
    except requests.HTTPError as e:
        status = e.response.status_code if e.response else 502
        detail = e.response.text if e.response else str(e)
        raise HTTPException(status_code=status, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=502, detail="Bridge unreachable") from e

    # Remove from local DB
    db.delete(ext)
    db.commit()

    return {"deleted": True, "id": account_id}


# ---------------------------------------------------------------------------
# Processor token creation (e.g. Finix)                                     
# ---------------------------------------------------------------------------


@router.post("/accounts/{account_id}/processor_token")
def create_processor_token(
    account_id: str,
    processor: str = "finix",
    db: Session = Depends(get_db),
    jwt=Depends(get_current_user),
):
    """Generate a Plaid *processor_token* for the given external account.

    The token is passed through to a payment processor (Finix, Stripe, etc.) so
    we never handle raw account & routing numbers ourselves.
    """

    # Authorize user & verify ownership of the external account
    user: User | None = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ext = (
        db.query(ExternalAccount)
        .filter(ExternalAccount.id == account_id, ExternalAccount.user_id == user.id)
        .first()
    )
    if not ext:
        raise HTTPException(status_code=404, detail="Account not found")

    # Fetch Plaid access_token for this external account
    item = db.query(PlaidItem).filter(PlaidItem.external_account_id == account_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Plaid token not found")

    try:
        token_resp = PlaidClient().create_processor_token(
            item.access_token, account_id=item.external_account_id or account_id, processor=processor
        )
    except requests.HTTPError as e:
        status = e.response.status_code if e.response else 502
        detail = e.response.text if e.response else str(e)
        raise HTTPException(status_code=status, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=502, detail="Plaid unreachable") from e

    # Don't persist locally yet – callers can cache if desired
    return token_resp 