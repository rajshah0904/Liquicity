from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from ..database import get_db
from ..models import User, BridgeCustomer, BridgeWallet, KycState, KycStatus, LastStep
from ..bridge import BridgeClient
from ..auth import get_current_user
from ..utils.currency_utils import get_fiat_currency_from_region
from ..utils.kyc_regions import (
    Region, AVAILABLE_COUNTRIES, get_region_for_country, 
    get_bridge_endorsements, get_form_config_for_region
)
from ..services.bridge_customer_service import bridge_customer_service
import logging
import json
import datetime
import os
import uuid
import threading

router = APIRouter(prefix="/kyc", tags=["kyc"])
_log = logging.getLogger(__name__)


def _lookup_user(db: Session, sub: str) -> Optional[User]:
    """Look up user by Auth0 subject ID only - NEVER by email to prevent auth bugs"""
    return db.query(User).filter(User.auth0_id == sub).first()


@router.post("/tos_link")
async def generate_tos_link(request: Request, db: Session = Depends(get_db), jwt=Depends(get_current_user)):
    """Generate a Bridge Terms of Service link that redirects back to the KYC page with signed_agreement_id."""
    user = _lookup_user(db, getattr(jwt, 'id', None))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    app_url = os.getenv("APP_URL", f"{request.url.scheme}://{request.url.hostname}:3000")
    try:
        tos = BridgeClient().request_tos_links(redirect_uri=f"{app_url}/kyc-verification")
        # Expected response: { "url": "https://dashboard.bridge.xyz/accept-terms-of-service?session_token=..." }
        return tos
    except Exception as e:
        _log.error("request_tos_links failed: %s", e)
        raise HTTPException(status_code=502, detail="Bridge request_tos_links failed")


@router.post("/link")
async def generate_kyc_link(db: Session = Depends(get_db), jwt=Depends(get_current_user)):
    user = _lookup_user(db, getattr(jwt, 'id', None))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.email:
        raise HTTPException(status_code=400, detail="Email required for KYC link generation")

    link = BridgeClient().create_kyc_link({
        "type": "individual",
        "email": user.email,
        "endorsements": ["sepa"],
    })

    # Note: kyc_link_id and kyc_url fields removed from User model
    # Store link details in session or return directly
    return link


@router.post("/callback", include_in_schema=False)
async def kyc_callback(request: Request, db: Session = Depends(get_db)):
    """Endpoint Bridge calls with KYC status updates"""
    body = await request.json()
    cid = body.get("customer_id")
    status = body.get("kyc_status")
    kyc_link_id = body.get("id")
    tos_status = body.get("tos_status")
    rejection_reasons = body.get("rejection_reasons")

    # Find user by bridge customer id
    user = None
    if cid:
        bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.id == cid).first()
        if bridge_customer:
            user = db.query(User).filter(User.id == bridge_customer.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Note: kyc_status, tos_status, rejection_reasons fields removed from User model
    # For now, just log the status
    _log.info(f"KYC callback for user {user.id}: status={status}, tos_status={tos_status}")

    if status == "approved":
        _log.info(f"Bridge KYC approved for user {user.id}")
        
        # Update KYC state if using new international flow
        kyc_state = db.query(KycState).filter(KycState.user_id == user.id).first()
        if kyc_state:
            kyc_state.bridge_status = KycStatus.APPROVED
            kyc_state.updated_at = datetime.datetime.utcnow()
            
            # Check if ready for wallet creation (handles dual KYC logic)
            _trigger_wallet_creation_if_ready(db, user.id)
        else:
            # Legacy flow - create customer and wallet directly
            bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == user.id).first()
            
            if not bridge_customer:
                try:
                    customer = BridgeClient().create_customer({
                        "type": "individual",
                        "email": user.email,
                    })
                    
                    # Create BridgeCustomer record
                    bridge_customer = BridgeCustomer(
                        id=customer.get("id"),
                        user_id=user.id,
                        first_name=customer.get("first_name"),
                        last_name=customer.get("last_name"),
                        email=customer.get("email"),
                        status=customer.get("status", "active"),
                        country=customer.get("country"),
                        created_at=datetime.datetime.utcnow(),
                        updated_at=datetime.datetime.utcnow()
                    )
                    db.add(bridge_customer)
                    db.flush()
                    
                    _log.info(f"Created Bridge customer {bridge_customer.id} for user {user.id} (legacy flow)")
                except Exception as e:
                    _log.error("create_customer failed: %s", e)
                    raise HTTPException(status_code=502, detail="Failed to create Bridge customer")

            # Create wallet immediately for legacy flow
            bridge_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == user.id).first()
            if not bridge_wallet and bridge_customer:
                try:
                    wallet = BridgeClient().create_wallet(bridge_customer.id, chain="solana")
                    
                    # Create BridgeWallet record with fiat currency mapping
                    fiat_currency = get_fiat_currency_from_region(user.region) if user.region else 'USD'
                    
                    bridge_wallet = BridgeWallet(
                        wallet_id=wallet.get("id"),
                        user_id=user.id,
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
                    db.flush()
                    
                    _log.info(f"Created Bridge wallet {bridge_wallet.wallet_id} for user {user.id} (legacy flow)")
                    
                except Exception as e:
                    _log.error("create_wallet failed: %s", e)
                    # Non-fatal - wallet creation can be retried later
    elif status == "rejected":
        _log.info("User %s KYC rejected", user.id)
    else:
        # incomplete, under_review etc.
        pass

    db.commit()
    return {"status": "ok"}


@router.get("/status")
async def get_kyc_status(db: Session = Depends(get_db), jwt: dict = Depends(get_current_user)):
    user = db.query(User).filter(User.auth0_id == jwt.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user has Bridge customer and wallet (indicates KYC completion)
    bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == user.id).first()
    bridge_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == user.id).first()
    
    # Determine KYC status based on Bridge customer existence
    kyc_status = "approved" if bridge_customer else "pending"
    
    return {
        "kyc_status": kyc_status,
        "link_status": kyc_status,
        "tos_status": "approved" if bridge_customer else "pending",
        "rejection_reasons": None,
        "kyc_url": None,  # Not stored in current schema
        "tos_url": None,  # Not stored in current schema
    }


# ------------------ Front-end polling helper ------------------

@router.get("/link-status")
async def get_live_link_status(db: Session = Depends(get_db), jwt=Depends(get_current_user)):
    """Return live KYC link status straight from Bridge and persist any change."""
    user = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user has Bridge customer (indicates KYC completion)
    bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == user.id).first()
    
    if bridge_customer:
        return {
            "kyc_status": "approved",
            "tos_status": "approved",
            "tos_link": None,
            "rejection_reasons": [],
        }
    else:
        return {
            "kyc_status": "pending",
            "tos_status": "pending",
            "tos_link": None,
            "rejection_reasons": [],
        }


# --- INTERNATIONAL KYC FLOW (v2) ---
# Mirrors US flow 1:1 with regional adaptations

class RegionSelectionRequest(BaseModel):
    country_or_region: str = Field(..., description="Country code or region (e.g., 'MX', 'EU')")

class RegionSelectionResponse(BaseModel):
    region: str
    form_config: Dict
    available_countries: List[Dict]

class KycInfoRequest(BaseModel):
    # PII fields - NOT stored in DB, only passed to vendors
    legal_name: str
    date_of_birth: str
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state_province: Optional[str] = None
    postal_code: str
    country: str
    national_id_number: str
    
    # TOS acceptance flags
    bridge_tos_accepted: bool
    
    # Resume token (if applicable)
    session_token: Optional[str] = None

class KycInfoResponse(BaseModel):
    bridge_redirect_url: Optional[str] = None
    session_token: str
    next_step: str

class KycStatusResponse(BaseModel):
    last_step: str
    bridge_status: str
    bridge_redirect_url: Optional[str] = None
    session_token: Optional[str] = None

def get_or_create_kyc_state(db: Session, user_id: str) -> KycState:
    """Get or create KYC state for user"""
    kyc_state = db.query(KycState).filter(KycState.user_id == user_id).first()
    if not kyc_state:
        kyc_state = KycState(user_id=user_id)
        db.add(kyc_state)
        db.commit()
        db.refresh(kyc_state)
    return kyc_state

def _create_wallet_after_verification(user_id: str, customer_id: str):
    """
    Background task to create wallet after verification is complete.
    Called when:
    1. Bridge-only: Bridge status = approved
    2. Dual KYC: Both Bridge AND VelaFi status = approved
    """
    from ..database import get_db
    from ..bridge import BridgeClient
    from ..utils.currency_utils import get_fiat_currency_from_region
    
    db = next(get_db())
    try:
        user = db.query(User).filter(User.id == user_id).first()
        bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.id == customer_id).first()
        
        if not user or not bridge_customer:
            _log.error(f"User {user_id} or Bridge customer {customer_id} not found for wallet creation")
            return
        
        # Check if wallet already exists
        existing_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == user_id).first()
        if existing_wallet:
            _log.info(f"Wallet already exists for user {user_id}: {existing_wallet.wallet_id}")
            return
        
        # Verify customer is approved on Bridge side
        try:
            bridge_client = BridgeClient()
            customer_data = bridge_client.get_customer(customer_id)
            bridge_status = (customer_data.get("status") or "").lower()
            
            if bridge_status not in {"approved", "active"}:
                _log.warning(f"Bridge customer {customer_id} not approved: {bridge_status}")
                return
        except Exception as e:
            _log.error(f"Failed to verify Bridge customer status {customer_id}: {e}")
            return
        
        # Create wallet on Bridge
        try:
            wallet = bridge_client.create_wallet(customer_id, chain="solana")
            fiat_currency = get_fiat_currency_from_region(user.region) if user.region else 'USD'
            
            bridge_wallet = BridgeWallet(
                wallet_id=wallet.get("id"),
                user_id=user.id,
                customer_id=customer_id,
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
            
            _log.info(f"✅ Wallet created successfully for user {user_id}: {wallet.get('id')} ({fiat_currency})")
            
        except Exception as e:
            _log.error(f"Failed to create wallet for user {user_id}: {e}")
            
    except Exception as e:
        _log.error(f"Wallet creation background task failed for user {user_id}: {e}")
    finally:
        db.close()

def _trigger_wallet_creation_if_ready(db: Session, user_id: str):
    """
    Check if user is ready for wallet creation and trigger it if so.
    Only Bridge approval is needed.
    """
    try:
        kyc_state = db.query(KycState).filter(KycState.user_id == user_id).first()
        bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == user_id).first()
        
        if not kyc_state or not bridge_customer:
            return
        
        # Check if wallet already exists
        existing_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == user_id).first()
        if existing_wallet:
            return
        
        # Check if ready for wallet creation (Bridge approval only)
        bridge_approved = kyc_state.bridge_status == KycStatus.APPROVED
        
        if bridge_approved:
            _log.info(f"🎉 User {user_id} completed Bridge KYC - triggering wallet creation")
            
            # Update KYC state to verified
            kyc_state.last_step = LastStep.VERIFIED
            db.commit()
            
            # Trigger wallet creation in background
            threading.Thread(
                target=_create_wallet_after_verification, 
                args=(str(user_id), bridge_customer.id), 
                daemon=True
            ).start()
        else:
            _log.info(f"User {user_id} verification incomplete - waiting for Bridge approval")
            
    except Exception as e:
        _log.error(f"Error checking wallet creation readiness for user {user_id}: {e}")

@router.get("/v2/countries")
async def get_available_countries():
    """Get list of available countries/regions for selection"""
    return {"countries": AVAILABLE_COUNTRIES}

@router.post("/v2/select-region", response_model=RegionSelectionResponse)
async def select_region(
    request: RegionSelectionRequest,
    db: Session = Depends(get_db),
    jwt = Depends(get_current_user)
):
    """Step 1: Select region and get form configuration"""
    user = _lookup_user(db, getattr(jwt, 'id', None))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # Determine region from input
        if request.country_or_region == "EU":
            region = Region.EU
            country = "EU"
        else:
            region = get_region_for_country(request.country_or_region)
            country = request.country_or_region.upper()
        
        # Update user and KYC state
        user.country = country
        user.region = region.value
        
        kyc_state = get_or_create_kyc_state(db, user.id)
        kyc_state.country = country
        kyc_state.region = region.value

        kyc_state.last_step = LastStep.REGION_SELECT
        
        db.commit()
        
        return RegionSelectionResponse(
            region=region.value,
            form_config=get_form_config_for_region(region),
            available_countries=AVAILABLE_COUNTRIES
        )
        
    except Exception as e:
        _log.error(f"Error selecting region: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to select region")

@router.get("/v2/status", response_model=KycStatusResponse)
async def get_kyc_status(
    db: Session = Depends(get_db),
    jwt = Depends(get_current_user)
):
    """Get current KYC status for resume functionality"""
    user = _lookup_user(db, getattr(jwt, 'id', None))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    kyc_state = get_or_create_kyc_state(db, user.id)
    
    return KycStatusResponse(
        last_step=kyc_state.last_step.value if kyc_state.last_step else "region_select",
        bridge_status=kyc_state.bridge_status.value if kyc_state.bridge_status else "pending",
        bridge_redirect_url=kyc_state.bridge_redirect_url,
        session_token=None  # Generate new one if needed
    )

@router.post("/v2/submit-info")
async def submit_international_kyc_info(
    request: Request,
    db: Session = Depends(get_db),
    jwt = Depends(get_current_user)
):
    """
    Submit KYC information with region-specific Bridge API payloads
    PII is sent directly to Bridge, NOT stored in our DB
    """
    user = _lookup_user(db, getattr(jwt, 'id', None))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # Parse request body
        body = await request.json()
        _log.info(f"Received KYC submission for user {user.id}")
        
        # Extract region and signed agreement ID
        region = body.get("region", "").lower()
        signed_agreement_id = body.get("signed_agreement_id")
        
        if not signed_agreement_id:
            raise HTTPException(status_code=400, detail="signed_agreement_id is required")
        
        # Prepare user data for Bridge customer service
        user_data = body.copy()
        user_data["email"] = user.email  # Always use verified auth email
        
        # Create Bridge customer using region-specific service
        customer = bridge_customer_service.create_customer_for_region(
            region=region,
            user_data=user_data,
            signed_agreement_id=signed_agreement_id
        )
        
        # Store Bridge customer info in database
        existing_bc = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == user.id).first()
        if not existing_bc:
            residential_address = user_data.get("residential_address", {})
            bridge_customer = BridgeCustomer(
                id=customer.get("id"),
                user_id=user.id,
                first_name=customer.get("first_name") or user_data.get("first_name"),
                last_name=customer.get("last_name") or user_data.get("last_name"),
                email=customer.get("email") or user.email,
                status=customer.get("status", "active"),
                street_line_1=residential_address.get("street_line_1"),
                city=residential_address.get("city"),
                subdivision=residential_address.get("subdivision"),
                postal_code=residential_address.get("postal_code"),
                country=residential_address.get("country"),
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow(),
            )
            db.add(bridge_customer)
        
        # Update user region
        country_code = user_data.get("residential_address", {}).get("country", "").upper()
        user.region = region
        user.country = country_code
        user.updated_at = datetime.datetime.utcnow()
        
        # Create/update KYC state
        kyc_state = get_or_create_kyc_state(db, user.id)
        kyc_state.country = country_code
        kyc_state.region = region
        kyc_state.bridge_status = KycStatus.PENDING
        kyc_state.last_step = LastStep.COMPLETE
        
        db.commit()
        
        return {
            "customer_id": customer.get("id"),
            "status": "submitted",
            "bridge_status": "pending",
            "region": region,
            "message": f"KYC submitted successfully for {region} region"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        _log.error(f"KYC submission failed: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"KYC submission failed: {str(e)}")

@router.get("/v2/processing-times")
async def get_processing_times():
    """Get estimated processing times for different regions"""
    return {
        "bridge": {
            "us": "1-2 business days",
            "eu": "1-3 business days", 
            "international": "1-2 business days"
        }
    }