from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models import User, Wallet
from pydantic import BaseModel, EmailStr
from typing import Dict, Any
import os
import uuid
import json
from dotenv import load_dotenv
from app.dependencies.auth import get_current_user  # Auth0 JWT validation
from app.services.bridge import BridgeClient
from datetime import datetime

load_dotenv()

router = APIRouter()

class Auth0UserCreate(BaseModel):
    email: EmailStr
    name: str
    auth0_id: str

# User Registration (Auth0 users only)
@router.post("/register", tags=["auth"])
async def register_auth0_user(user: Auth0UserCreate, db: Session = Depends(get_db)):
    try:
        # Ensure email is unique
        existing = db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": user.email}).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Generate unique wallet address
        wallet_address = str(uuid.uuid4())
        
        # Create user record
        result = db.execute(
            text("""
                INSERT INTO users (
                  email, first_name, last_name, auth0_id, account_type, wallet_address
                ) VALUES (
                  :email, :first_name, :last_name, :auth0_id, :account_type, :wallet_address
                ) RETURNING id
            """),
            {
                "email": user.email,
                "first_name": user.name.split()[0],
                "last_name": " ".join(user.name.split()[1:]),
                "auth0_id": user.auth0_id,
                "account_type": "auth0",
                "wallet_address": wallet_address
            }
        )
        db.commit()
        user_id = result.first()[0]
        return {"id": user_id, "email": user.email, "wallet_address": wallet_address, "message": "User registered successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error registering Auth0 user: {e}")

# KYC Submission
@router.post("/kyc/submit", tags=["kyc"])
async def submit_kyc(request: Request, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    form = await request.form()

    # Lookup user by email or Auth0 ID
    row = db.execute(
        text("SELECT id FROM users WHERE email = :email OR auth0_id = :auth0_id"),
        {"email": current_user, "auth0_id": current_user}
        ).first()
    if not row:
        # Create minimal user record using data from KYC form
        first_name = form.get("first_name") or ""
        last_name = form.get("last_name") or ""
        wallet_address = str(uuid.uuid4())
        email_candidate = current_user if "@" in current_user else None
        auth0_candidate = None if email_candidate else current_user

        if email_candidate is None:
            email_candidate = form.get("email")
        if not email_candidate:
            raise HTTPException(status_code=400, detail="Email address is required but missing from Auth0 and form")

        insert_res = db.execute(
            text("""
                INSERT INTO users (email, first_name, last_name, auth0_id, wallet_address, account_type)
                VALUES (:email, :first_name, :last_name, :auth0_id, :wallet, 'auth0') RETURNING id
            """),
            {
                "email": email_candidate,
                "first_name": first_name,
                "last_name": last_name,
                "auth0_id": auth0_candidate,
                "wallet": wallet_address,
            },
        )
        db.commit()
        user_id = insert_res.first()[0]
    else:
        user_id = row[0]

    # Collect KYC data and save file uploads
    kyc_country = form.get("kyc_country")

    if not kyc_country:
        raise HTTPException(status_code=400, detail="kyc_country is required")

    # ------------------------------------------------------------------
    # Country-specific required fields (Bridge compliance)
    # ------------------------------------------------------------------
    USA_FIELDS = {
        "required": [
            "first_name",
            "last_name",
            "date_of_birth",
            "street_address",
            "city",
            "state",
            "postal_code",
            "email",
            "id_number",  # SSN stored in generic id_number
        ],
        "id_type": "ssn",
    }

    EU_FIELDS = {
        "required": [
            "first_name",
            "last_name",
            "date_of_birth",
            "street_address",
            "city",
            "state",  # region / province
            "postal_code",
            "email",
            "id_number",
            "country_of_residence",
        ],
    }

    NON_US_FIELDS = {
        "required": [
            "first_name",
            "last_name",
            "date_of_birth",
            "street_address",
            "city",
            "postal_code",
            "state",  # province / state analogue
            "email",
            "id_number",  # national identity number
        ],
    }

    EU_COUNTRIES = {
        "AT","BE","BG","CH","CY","CZ","DE","DK","EE","ES","FI","FR","GB","GR","HR","HU","IE","IS","IT","LI","LT","LU","LV","MT","NL","NO","PL","PT","RO","SE","SI","SK"
    }

    country_upper = kyc_country.upper()
    if country_upper == "US":
        field_spec = USA_FIELDS
    elif country_upper == "EU":
        field_spec = EU_FIELDS
    else:
        field_spec = NON_US_FIELDS

    missing = [fld for fld in field_spec["required"] if form.get(fld) is None and not any(isinstance(v, UploadFile) and k.startswith(fld) for k,v in form.multi_items())]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required KYC fields: {', '.join(missing)}")

    kyc_data: Dict[str, Any] = {}
    upload_dir = "static/kyc_photos"
    os.makedirs(upload_dir, exist_ok=True)

    for field, value in form.multi_items():
        if field == "kyc_country":
            continue
        if isinstance(value, UploadFile):
            ext = os.path.splitext(value.filename)[1]
            fname = f"{user_id}_{uuid.uuid4()}{ext}"
            path = os.path.join(upload_dir, fname)
            data = await value.read()
            with open(path, "wb") as f:
                f.write(data)
            kyc_data[field] = fname
        else:
            kyc_data[field] = value

    # Default id_type if not provided
    if "id_type" not in kyc_data:
        if country_upper == "US":
            kyc_data["id_type"] = "ssn"
        else:
            kyc_data["id_type"] = "national_id"

    # Compute extra_data for any dynamic fields not part of standard set
    standard_cols = {
        "full_name",
        "first_name",
        "last_name",
        "date_of_birth",
        "street_address",
        "city",
        "state",
        "postal_code",
        "id_type",
        "id_number",
        "photo",
        "proof_of_address",
    }
    extra_data_dict = {k: v for k, v in kyc_data.items() if k not in standard_cols}

    # -------------------------------------------------------------
    # Build Bridge Customers API payload for future submission
    # -------------------------------------------------------------

    # Helper to convert ISO-3166 alpha-2 -> alpha-3 when needed
    ISO2_TO_3 = {
        "US": "USA", "GB": "GBR", "DE": "DEU", "FR": "FRA", "ES": "ESP", "IT": "ITA",
        "IE": "IRL", "NL": "NLD", "BE": "BEL", "AT": "AUT", "CH": "CHE", "DK": "DNK",
        "FI": "FIN", "SE": "SWE", "NO": "NOR", "PL": "POL", "PT": "PRT", "CZ": "CZE",
        "SK": "SVK", "SI": "SVN", "HR": "HRV", "RO": "ROU", "BG": "BGR", "EE": "EST",
        "LT": "LTU", "LV": "LVA", "CY": "CYP", "MT": "MLT", "LI": "LIE", "IS": "ISL",
        "HU": "HUN", "GR": "GRC", "LU": "LUX", "MX": "MEX"
    }

    def to_iso3(code: str | None) -> str | None:
        if not code:
            return None
        c = code.upper()
        if len(c) == 2:
            return ISO2_TO_3.get(c, c)
        return c  # assume already iso-3

    # Build the address object
    address_obj: Dict[str, Any] = {
        "street_line_1": kyc_data.get("street_address"),
        "city": kyc_data.get("city"),
        "subdivision": kyc_data.get("state"),  # already expects the subdivision w/o country prefix
        "postal_code": kyc_data.get("postal_code"),
        "country": to_iso3("USA" if country_upper == "US" else (kyc_data.get("country_of_residence") or kyc_country))
    }
    # Optional second address line
    if kyc_data.get("street_address_2"):
        address_obj["street_line_2"] = kyc_data.get("street_address_2")

    bridge_payload: Dict[str, Any] = {
        "type": "individual",
        "first_name": kyc_data.get("first_name"),
        "last_name": kyc_data.get("last_name"),
        "email": extra_data_dict.get("email") if extra_data_dict else None,
        "address": address_obj,
        "birth_date": kyc_data.get("date_of_birth"),
        # signed_agreement_id excluded for EU/ROW as per updated requirements
        "identifying_information": [],
        "endorsements": [],
    }

    # Endorsement logic per country
    if country_upper == "US":
        bridge_payload["endorsements"] = ["base"]
    elif country_upper in EU_COUNTRIES or country_upper == "EU":
        bridge_payload["endorsements"] = ["sepa"]
    elif country_upper == "MX":
        bridge_payload["endorsements"] = ["spei"]
        if kyc_data.get("tax_identification_number") or kyc_data.get("rfc"):
            bridge_payload["tax_identification_number"] = kyc_data.get("tax_identification_number") or kyc_data.get("rfc")

    # Build generic ID dict
    if kyc_data.get("id_type") and kyc_data.get("id_number"):
        id_dict: Dict[str, Any] = {
            "type": kyc_data["id_type"],
            "issuing_country": to_iso3((kyc_data.get("country_of_residence") or kyc_country)).lower(),
            "number": kyc_data["id_number"],
        }
        if kyc_data.get("id_image_front"):
            id_dict["image_front"] = kyc_data.get("id_image_front")
        if kyc_data.get("id_image_back"):
            id_dict["image_back"] = kyc_data.get("id_image_back")
        bridge_payload["identifying_information"].append(id_dict)

    # If proof_of_address uploaded include in documents list
    if kyc_data.get("proof_of_address"):
        bridge_payload["documents"] = [{
            "purposes": ["proof_of_address"],
            "file": kyc_data.get("proof_of_address")  # path placeholder; later convert to data-uri
        }]

    # Store bridge_payload inside extra_data for now
    extra_data_dict = extra_data_dict or {}
    extra_data_dict["bridge_payload"] = bridge_payload

    # Update user row pre-emptively to not_started while we talk to Bridge
    db.execute(
        text("UPDATE users SET kyc_status = :status WHERE id = :uid"),
        {"status": "not_started", "uid": user_id},
    )

    # Send to Bridge if API key configured
    client = BridgeClient()
    try:
        bridge_resp = await client.create_customer(bridge_payload)
        # Update user record with Bridge info
        db.execute(
            text("UPDATE users SET bridge_customer_id = :cid, kyc_status = :status, endorsement_status = :endorse WHERE id = :uid"),
            {
                "cid": bridge_resp.get("id"),
                "status": bridge_resp.get("kyc_status"),
                "endorse": json.dumps(bridge_resp.get("endorsements")) if bridge_resp.get("endorsements") else None,
                "uid": user_id,
            },
        )
        db.commit()
        # Issue card
        try:
            card = await client.create_card(bridge_resp.get('id'), {"type":"virtual","currency":"usdb"})
            db.execute(text("""INSERT INTO card_accounts (user_id, bridge_card_id, last4, state) VALUES (:u,:cid,:l4,:st) ON CONFLICT DO NOTHING"""),{"u":user_id,"cid":card.get('id'),"l4":card.get('last4'),"st":card.get('state')})
        except Exception:
            pass
    except Exception as e:
        # Log but do not fail submission
        import logging
        logging.getLogger(__name__).error("Bridge create_customer failed: %s", e)

    return {"message": "KYC submitted successfully", "user_id": user_id}

# === New Helper Models ===
class UserProfileOut(BaseModel):
    """Shape returned for current user profile requests."""
    id: int
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    auth0_id: str | None = None
    country: str | None = None
    is_verified: bool | None = None

class UserProfileUpdate(BaseModel):
    """Fields a user is allowed to update on their profile."""
    first_name: str | None = None
    last_name: str | None = None
    country: str | None = None

# === Utility ===

def _lookup_user_row(db: Session, identifier: str):
    """Return a (row) for a given email or auth0_id, or None."""
    return db.execute(
        text("SELECT * FROM users WHERE email = :id OR auth0_id = :id"),
        {"id": identifier},
    ).first()

# === Compatibility alias for trailing slash on register ===
@router.post("/register/", tags=["auth"], include_in_schema=False)
async def register_auth0_user_slash(user: Auth0UserCreate, db: Session = Depends(get_db)):
    """Alias so /user/register/ also works."""
    return await register_auth0_user(user, db)  # type: ignore

# === Check if current authenticated user exists & KYC status ===
@router.get("/check", tags=["auth"])
async def check_user(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    row = _lookup_user_row(db, current_user)
    exists = bool(row)
    kyc_complete = bool(row and row._mapping.get("kyc_status") in ("approved", "active"))
    return {"exists": exists, "kyc_complete": kyc_complete}

# === Get current user profile ===
@router.get("/user", response_model=UserProfileOut, tags=["auth"])
@router.get("/user/", response_model=UserProfileOut, tags=["auth"], include_in_schema=False)
async def get_current_user_profile(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    row = _lookup_user_row(db, current_user)
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    user_dict = dict(row._mapping)
    return {
        "id": user_dict["id"],
        "email": user_dict["email"],
        "first_name": user_dict.get("first_name"),
        "last_name": user_dict.get("last_name"),
        "auth0_id": user_dict.get("auth0_id"),
        "country": user_dict.get("country"),
        "is_verified": user_dict.get("is_verified"),
    }

# === Update profile endpoint ===
@router.put("/update-profile/{user_id}", tags=["auth"])
async def update_profile(
    user_id: str,
    profile: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    # Ensure the current user matches the record they are trying to update
    row = _lookup_user_row(db, current_user)
    if not row or str(row[0]) != user_id:
        raise HTTPException(status_code=403, detail="Not authorised to update this profile")

    update_fields = []
    params: dict[str, str | int] = {"user_id": user_id}

    if profile.first_name is not None:
        update_fields.append("first_name = :first_name")
        params["first_name"] = profile.first_name
    if profile.last_name is not None:
        update_fields.append("last_name = :last_name")
        params["last_name"] = profile.last_name
    if profile.country is not None:
        update_fields.append("country = :country")
        params["country"] = profile.country

    if not update_fields:
        return {"message": "No changes"}

    db.execute(
        text(f"UPDATE users SET {', '.join(update_fields)} WHERE id = :user_id"),
        params,
    )
    db.commit()

    return {"success": True, "message": "Profile updated"}

# === KYC status endpoint ===
@router.get("/kyc/{user_id}/status", tags=["kyc"])
async def get_kyc_status(user_id: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    """Return KYC verification status for the requested user (must be the same authenticated user)."""
    # Ensure requester is querying their own record unless later we add admin check
    row = db.execute(text("SELECT id FROM users WHERE id::text = :uid"), {"uid": user_id}).first()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    # Ensure JWT subject matches this user
    requester = _lookup_user_row(db, current_user)
    if not requester or str(requester[0]) != user_id:
        raise HTTPException(status_code=403, detail="Not authorised to view KYC status for this user")

    usr = db.execute(text("SELECT bridge_customer_id, kyc_status, endorsement_status FROM users WHERE id::text = :uid"), {"uid": user_id}).first()
    if not usr or not usr[1]:
        return {"verification_status": "unsubmitted"}
    kyc_complete = row and bool(row["kyc_status"] in ("approved", "active"))
    return {
        "verification_status": usr[1],
        "bridge_customer_id": usr[0],
        "endorsement_status": usr[2],
    }

# === Public endpoint: check if email already registered ===
# This is unauthenticated so we can prevent duplicate sign-ups before hitting Auth0
@router.get("/email-exists", tags=["auth"], summary="Check if email is already registered (public)")
async def email_exists(email: EmailStr, db: Session = Depends(get_db)):
    row = db.execute(text("SELECT 1 FROM users WHERE lower(email) = lower(:e)"), {"e": email}).first()
    return {"exists": bool(row)}
