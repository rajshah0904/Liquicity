from fastapi import APIRouter, Depends, Response, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db, SessionLocal
from ..models import User, BridgeCustomer, BridgeWallet
from ..auth import get_current_user
from fastapi_auth0.auth import Auth0User
from sqlalchemy import func
from ..bridge import BridgeClient
from ..utils.currency_utils import get_fiat_currency_from_region
import logging
import datetime
import threading
import time

router = APIRouter(tags=["auth"])
_log = logging.getLogger(__name__)


def _user_by_sub(db: Session, sub: str):
    """Look up user by Auth0 subject ID only - NEVER by email to prevent auth bugs"""
    return db.query(User).filter(User.auth0_id == sub).first()


def _await_customer_and_ensure_wallet(user_id: str, customer_id: str):
    """Poll Bridge for customer status until active/approved, then ensure wallet exists/imported.
    Runs in a background thread; uses its own DB session.
    """
    db = SessionLocal()
    try:
        attempts = 20
        delay = 3
        client = BridgeClient()
        for _ in range(attempts):
            try:
                data = client.get_customer(customer_id)
                status = (data.get("status") or "").lower()
                if status in {"active", "approved"}:
                    break
            except Exception as e:
                _log.warning(f"get_customer poll failed for user {user_id}: {e}")
            time.sleep(delay)
        # Refresh db_user and bridge_customer
        db_user = db.query(User).filter(User.id == user_id).first()
        bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.id == customer_id).first()
        if not db_user or not bridge_customer:
            return
        # If wallet already exists in our DB, done
        existing_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == db_user.id).first()
        if existing_wallet:
            return
        # Try to import existing wallet from Bridge
        try:
            wallets_list = client.list_customer_wallets(bridge_customer.id) or {}
            items = wallets_list.get("data", []) if isinstance(wallets_list, dict) else []
            if items:
                w = items[0]
                fiat_currency = get_fiat_currency_from_region(db_user.region) if db_user.region else 'USD'
                imported = BridgeWallet(
                    wallet_id=w.get("id"),
                    user_id=db_user.id,
                    customer_id=bridge_customer.id,
                    chain=w.get("chain", "solana"),
                    address=w.get("address"),
                    balances=w.get("balances", []),
                    fiat_currency=fiat_currency,
                    fiat_balance_by_rate={},
                    created_at=datetime.datetime.utcnow(),
                    updated_at=datetime.datetime.utcnow(),
                )
                db.add(imported)
                db.commit()
                return
        except Exception as e:
            _log.warning(f"Import existing wallet failed for user {user_id}: {e}")
        # Create new wallet if none on Bridge
        try:
            wallet = client.create_wallet(bridge_customer.id, chain="solana")
            fiat_currency = get_fiat_currency_from_region(db_user.region) if db_user.region else 'USD'
            bridge_wallet = BridgeWallet(
                wallet_id=wallet.get("id"),
                user_id=db_user.id,
                customer_id=bridge_customer.id,
                chain=wallet.get("chain", "solana"),
                address=wallet.get("address"),
                balances=wallet.get("balances", []),
                fiat_currency=fiat_currency,
                fiat_balance_by_rate={},
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            )
            db.add(bridge_wallet)
            db.commit()
        except Exception as e:
            _log.error(f"Background wallet create failed for user {user_id}: {e}")
    finally:
        db.close()


@router.get("/user/check")
async def user_check(db: Session = Depends(get_db), auth_user: Auth0User = Depends(get_current_user)):
    """Return comprehensive user onboarding state for proper flow resumption."""
    
    # DEBUG: Log the Auth0 user info
    _log.info(f"user_check called with Auth0 user: id={auth_user.id}, email={auth0_user_email if (auth0_user_email := getattr(auth_user, 'email', None)) else None}")
    
    db_user = _user_by_sub(db, auth_user.id)
    
    if not db_user:
        _log.info(f"No user found for Auth0 ID: {auth_user.id}")
        return {"exists": False, "next_step": "register"}
    
    _log.info(f"Found existing user: {db_user.email} (ID: {db_user.id})")
    
    # Get related onboarding data
    bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == db_user.id).first()
    bridge_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == db_user.id).first()
    
    # Determine current onboarding state and next step
    if not bridge_customer:
        return {
            "exists": True,
            "next_step": "kyc",
            "user_id": str(db_user.id),
            "email": db_user.email,
            "completed_steps": ["register"]
        }
    elif bridge_customer and not bridge_wallet:
        return {
            "exists": True,
            "next_step": "create_wallet",
            "user_id": str(db_user.id),
            "email": db_user.email,
            "completed_steps": ["register", "kyc"]
        }
    else:
        return {
            "exists": True,
            "next_step": "done",
            "user_id": str(db_user.id),
            "email": db_user.email,
            "completed_steps": ["register", "kyc", "create_wallet"]
        }


@router.options("/user/check")
async def options_user_check() -> Response:
    # Allow preflight requests
    return Response(status_code=200)


# -------------------- KYC submission → Bridge customer creation --------------------
@router.post("/user/kyc/submit")
async def kyc_submit(request: Request, db: Session = Depends(get_db), auth_user: Auth0User = Depends(get_current_user)):
    """
    Accepts KYC payload from frontend, creates Bridge customer, persists BridgeCustomer with address
    fields, sets user's region at this time (not before), and creates Bridge wallet with fiat currency
    derived from region.
    """
    db_user = _user_by_sub(db, auth_user.id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    # Required top-level fields
    first_name = body.get("first_name")
    last_name = body.get("last_name")
    birth_date = body.get("birth_date")  # Not directly stored in our DB schema, but sent to Bridge
    residential_address = body.get("residential_address") or {}
    identifying_information = body.get("identifying_information") or []
    region = (body.get("region") or "").lower()  # e.g. 'us', 'eu', etc.

    # Basic validation (frontend already validates, this is defensive)
    missing = [f for f in [
        ("first_name", first_name),
        ("last_name", last_name),
        ("residential_address", residential_address),
    ] if not f[1]]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing fields: {', '.join(k for k, _ in missing)}")

    # Compose Bridge payload
    bridge_payload = {
        "type": "individual",
        "first_name": first_name,
        "last_name": last_name,
        "email": db_user.email,  # Always use verified auth email
        "birth_date": birth_date,
        "residential_address": {
            "street_line_1": residential_address.get("street_line_1"),
            "city": residential_address.get("city"),
            "subdivision": residential_address.get("subdivision"),
            "postal_code": residential_address.get("postal_code"),
            "country": residential_address.get("country"),
        },
        "signed_agreement_id": body.get("signed_agreement_id"),
        "identifying_information": identifying_information,
    }

    # Call Bridge to create the customer
    try:
        customer = BridgeClient().create_customer(bridge_payload)
    except Exception as e:
        _log.error("Bridge create_customer failed: %s", e)
        raise HTTPException(status_code=502, detail="Bridge create_customer failed")

    # Persist BridgeCustomer
    existing_bc = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == db_user.id).first()
    if existing_bc:
        persisted_customer = existing_bc
    else:
        persisted_customer = BridgeCustomer(
            id=customer.get("id"),
            user_id=db_user.id,
            first_name=customer.get("first_name") or first_name,
            last_name=customer.get("last_name") or last_name,
            email=customer.get("email") or db_user.email,
            status=customer.get("status", "active"),
            # Address fields from submission
            street_line_1=bridge_payload["residential_address"].get("street_line_1"),
            city=bridge_payload["residential_address"].get("city"),
            subdivision=bridge_payload["residential_address"].get("subdivision"),
            postal_code=bridge_payload["residential_address"].get("postal_code"),
            country=bridge_payload["residential_address"].get("country"),
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )
        db.add(persisted_customer)

    # Persist region on the user NOW (KYC is being submitted/created)
    if region:
        db_user.region = region
        db_user.updated_at = datetime.datetime.utcnow()

    db.commit()

    # Fire-and-forget background task to await activation and ensure wallet exists
    threading.Thread(target=_await_customer_and_ensure_wallet, args=(str(db_user.id), persisted_customer.id), daemon=True).start()

    return {
        "customer_id": persisted_customer.id,
        "status": "created"
    }


@router.post("/user/create-wallet")
async def create_wallet_if_approved(db: Session = Depends(get_db), auth_user: Auth0User = Depends(get_current_user)):
    """Create wallet automatically if user has approved KYC but no wallet exists.
    Idempotent behavior: if our DB lacks a wallet, we check Bridge for existing wallets first and import them.
    """
    
    db_user = _user_by_sub(db, auth_user.id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == db_user.id).first()
    if not bridge_customer:
        raise HTTPException(status_code=400, detail="Bridge customer not found")
    
    # If wallet already exists in our DB, return
    existing_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == db_user.id).first()
    if existing_wallet:
        return {
            "wallet_created": False,
            "message": "Wallet already exists",
            "wallet_id": existing_wallet.wallet_id,
            "fiat_currency": existing_wallet.fiat_currency,
        }
    
    # Ensure Bridge customer is active/approved
    customer_data = BridgeClient().get_customer(bridge_customer.id)
    status = (customer_data.get("status") or "").lower()
    if status not in {"approved", "active"}:
        raise HTTPException(status_code=400, detail=f"KYC not approved/active. Status: {customer_data.get('status')}")
    
    # Check Bridge for existing wallets and import the first one
    try:
        wallets_list = BridgeClient().list_customer_wallets(bridge_customer.id) or {}
        items = wallets_list.get("data", []) if isinstance(wallets_list, dict) else []
        if items:
            w = items[0]
            fiat_currency = get_fiat_currency_from_region(db_user.region) if db_user.region else 'USD'
            imported = BridgeWallet(
                wallet_id=w.get("id"),
                user_id=db_user.id,
                customer_id=bridge_customer.id,
                chain=w.get("chain", "solana"),
                address=w.get("address"),
                balances=w.get("balances", []),
                fiat_currency=fiat_currency,
                fiat_balance_by_rate={},
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow(),
            )
            db.add(imported)
            db.commit()
            return {
                "wallet_created": False,
                "message": "Imported existing Bridge wallet",
                "wallet_id": imported.wallet_id,
                "fiat_currency": imported.fiat_currency,
            }
    except Exception as e:
        _log.error(f"Failed to import existing Bridge wallets for user {db_user.id}: {e}")
        # continue to create
    
    # Create a new wallet on Bridge
    try:
        wallet = BridgeClient().create_wallet(bridge_customer.id, chain="solana")
        fiat_currency = get_fiat_currency_from_region(db_user.region) if db_user.region else 'USD'
        bridge_wallet = BridgeWallet(
            wallet_id=wallet.get("id"),
            user_id=db_user.id,
            customer_id=bridge_customer.id,
            chain=wallet.get("chain", "solana"),
            address=wallet.get("address"),
            balances=wallet.get("balances", []),
            fiat_currency=fiat_currency,
            fiat_balance_by_rate={},
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow()
        )
        db.add(bridge_wallet)
        db.commit()
        _log.info(f"Created Bridge wallet {bridge_wallet.wallet_id} for user {db_user.id}")
        return {
            "wallet_created": True,
            "wallet_id": bridge_wallet.wallet_id,
            "fiat_currency": fiat_currency,
            "message": "Wallet created successfully"
        }
    except Exception as e:
        _log.error(f"Failed to create wallet for user {db_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create wallet")


@router.get("/user/email-exists")
async def email_exists(email: str, db: Session = Depends(get_db)):
    """Public endpoint to check whether an account already exists for the given email address."""
    exists = bool(db.query(User).filter(func.lower(User.email) == email.lower()).first())
    return {"exists": exists} 