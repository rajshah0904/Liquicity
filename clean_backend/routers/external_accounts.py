from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import requests
from typing import List, Dict, Optional
import logging, json

from ..database import get_db
from ..auth import get_current_user
from ..models import User, ExternalAccount, BridgeCustomer
from ..bridge import BridgeClient
from ..services.plaid_client import PlaidClient
from ..models import PlaidItem

router = APIRouter(prefix="/external_accounts", tags=["external_accounts"])

class PublicTokenSchema(BaseModel):
    public_token: str
    institution_name: Optional[str] = None  # From Plaid Link metadata
    institution_id: Optional[str] = None    # From Plaid Link metadata

# Helper functions for Option A flow
import re

def normalize_name_tokens(name: str) -> set:
    """Tokenize and normalize a name: split on whitespace, remove punctuation, lowercase."""
    if not name:
        return set()
    
    # Remove punctuation and split on whitespace
    cleaned = re.sub(r'[^\w\s]', '', name.strip())
    tokens = cleaned.lower().split()
    return set(tokens)

def jaro_winkler_similarity(s1: str, s2: str) -> float:
    """Simple Jaro-Winkler similarity implementation."""
    if not s1 or not s2:
        return 0.0
    if s1 == s2:
        return 1.0
    
    # Simple character-based similarity (approximation)
    len1, len2 = len(s1), len(s2)
    match_window = max(len1, len2) // 2 - 1
    match_window = max(0, match_window)
    
    s1_matches = [False] * len1
    s2_matches = [False] * len2
    matches = 0
    
    # Find matches
    for i in range(len1):
        start = max(0, i - match_window)
        end = min(i + match_window + 1, len2)
        for j in range(start, end):
            if s2_matches[j] or s1[i] != s2[j]:
                continue
            s1_matches[i] = s2_matches[j] = True
            matches += 1
            break
    
    if matches == 0:
        return 0.0
    
    # Calculate Jaro similarity
    jaro = (matches / len1 + matches / len2 + (matches - 0) / matches) / 3.0
    return jaro

def verify_identity_advanced(bridge_first: str, bridge_last: str, plaid_names: List[str]) -> tuple[bool, str]:
    """Advanced identity verification with tokenization and fuzzy matching fallback."""
    if not bridge_first or not bridge_last:
        return False, "Incomplete Bridge customer name data"
    
    # Normalize Bridge names
    bridge_first_tokens = normalize_name_tokens(bridge_first)
    bridge_last_tokens = normalize_name_tokens(bridge_last)
    
    # Try exact token matching first
    for plaid_name in plaid_names:
        plaid_tokens = normalize_name_tokens(plaid_name)
        
        # Check if both first and last name tokens appear in Plaid tokens
        first_match = bool(bridge_first_tokens.intersection(plaid_tokens))
        last_match = bool(bridge_last_tokens.intersection(plaid_tokens))
        
        if first_match and last_match:
            return True, f"Exact token match: '{plaid_name}' contains both '{bridge_first}' and '{bridge_last}'"
    
    # Fallback: Fuzzy matching with high threshold
    fuzzy_threshold = 0.90
    
    for plaid_name in plaid_names:
        plaid_tokens = list(normalize_name_tokens(plaid_name))
        
        # Find best match for first name
        best_first_score = 0.0
        for token in plaid_tokens:
            score = jaro_winkler_similarity(list(bridge_first_tokens)[0] if bridge_first_tokens else "", token)
            best_first_score = max(best_first_score, score)
        
        # Find best match for last name  
        best_last_score = 0.0
        for token in plaid_tokens:
            score = jaro_winkler_similarity(list(bridge_last_tokens)[0] if bridge_last_tokens else "", token)
            best_last_score = max(best_last_score, score)
        
        if best_first_score >= fuzzy_threshold and best_last_score >= fuzzy_threshold:
            return True, f"Fuzzy match: '{plaid_name}' (first: {best_first_score:.3f}, last: {best_last_score:.3f})"
    
    return False, f"No match found for '{bridge_first} {bridge_last}' in Plaid names: {plaid_names}"

# --- Helpers: Country normalization for IBAN (ISO2 → ISO3) ---
_ISO2_TO_ISO3: Dict[str, str] = {
    # Enabled Plaid EU markets (only these are mapped/enabled)
    "AT": "AUT",
    "BE": "BEL",
    "DK": "DNK",
    "EE": "EST",
    "FI": "FIN",
    "FR": "FRA",
    "DE": "DEU",
    "IE": "IRL",
    "IT": "ITA",
    "LV": "LVA",
    "LT": "LTU",
    "NO": "NOR",
    "PL": "POL",
    "PT": "PRT",
    "ES": "ESP",
    "SE": "SWE",
    "NL": "NLD",
}

# Restrict allowed ISO2 countries to the same list for Plaid link token creation
_ALLOWED_EU_ISO2: List[str] = list(_ISO2_TO_ISO3.keys())

def _iso2_to_iso3(code: Optional[str]) -> Optional[str]:
    if not code:
        return None
    return _ISO2_TO_ISO3.get(code.upper())

def _derive_iban_country(iban_entry: Dict[str, str]) -> str:
    """Return ISO3 country for IBAN. Prefer provided fields, else parse IBAN prefix.

    Bridge requires ISO3 (alpha-3). If we cannot determine, return empty string.
    """
    provided = (iban_entry.get("iban_country") or iban_entry.get("country") or "").strip()
    if len(provided) == 3:
        return provided.upper()
    if len(provided) == 2:
        iso3 = _iso2_to_iso3(provided)
        return iso3 or provided.upper()
    iban = (iban_entry.get("iban") or "").strip()
    if len(iban) >= 2:
        iso2 = iban[:2]
        iso3 = _iso2_to_iso3(iso2)
        return iso3 or iso2.upper()
    return ""

def map_plaid_to_bridge_external_account(
    plaid_auth: Dict, plaid_identity: Dict, bridge_customer: BridgeCustomer, account_id: str, institution_name: Optional[str] = None
) -> Dict[str, any]:
    """Map Plaid Auth + Identity data to Bridge external account creation format."""
    
    # Find the specific account in Plaid auth response
    plaid_account = None
    for acc in plaid_auth.get("accounts", []):
        if acc.get("account_id") == account_id:
            plaid_account = acc
            break
    
    if not plaid_account:
        raise ValueError(f"Account {account_id} not found in Plaid auth response")
    
    # Get ACH transfer codes from Auth response
    ach_data = None
    for acc in plaid_auth.get("numbers", {}).get("ach", []):
        if acc.get("account_id") == account_id:
            ach_data = acc
            break
    
    if not ach_data:
        raise ValueError(f"No ACH transfer codes found for account {account_id}")
    
    # Get identity info for the account
    identity_account = None
    for acc in plaid_identity.get("accounts", []):
        if acc.get("account_id") == account_id:
            identity_account = acc
            break
    
    # Extract address from identity (use first owner's mailing address)
    address = {}
    if identity_account and identity_account.get("owners"):
        owner = identity_account["owners"][0]
        mailing_addr = owner.get("mailing_address", {})
        if mailing_addr:
            # Extract state from region (format: "US-CA" -> "CA")
            region = mailing_addr.get("region", "")
            state = region.split("-")[-1] if "-" in region else region
            
            # Get street address from lines array
            street_lines = mailing_addr.get("lines", [])
            street_line_1 = street_lines[0] if street_lines else ""
            
            address = {
                "street_line_1": street_line_1,
                "city": mailing_addr.get("city", ""),
                "state": state,
                "postal_code": mailing_addr.get("postal_code", ""),
                "country": "USA"  # Convert from ISO to full name
            }
    
    # Use institution name from Plaid Link metadata
    bank_name = institution_name if institution_name and institution_name != "Unknown Bank" else "Bank"
    
    # Build Bridge external account payload
    payload = {
        "currency": "usd",
        "account_type": "us", 
        "bank_name": bank_name,
        "account_name": f"{bank_name} {plaid_account.get('subtype', 'Account').title()}",
        "first_name": bridge_customer.first_name or "",
        "last_name": bridge_customer.last_name or "",
        "account_owner_type": "individual",
        "account_owner_name": f"{bridge_customer.first_name or ''} {bridge_customer.last_name or ''}".strip(),
        "account": {
            "routing_number": ach_data.get("routing", ""),  # Plaid uses 'routing', not 'routing_number'
            "account_number": ach_data.get("account", ""),  # Plaid uses 'account', not 'account_number'
            "checking_or_savings": "checking" if plaid_account.get("subtype") == "checking" else "savings"
        }
    }
    
    # Add address - try Plaid Identity first, fallback to Bridge customer address
    if address and any(address.values()):
        payload["address"] = address
    elif (bridge_customer.street_line_1 and bridge_customer.city and 
          bridge_customer.subdivision and bridge_customer.postal_code and bridge_customer.country):
        # Use fallback address from our KYC database
        payload["address"] = {
            "street_line_1": bridge_customer.street_line_1,
            "city": bridge_customer.city,
            "state": bridge_customer.subdivision,  # Convert subdivision to state for Bridge API
            "postal_code": bridge_customer.postal_code,
            "country": "USA" if bridge_customer.country == "USA" else bridge_customer.country
        }
    else:
        pass # No address available from Plaid Identity or Bridge customer database
    
    return payload

@router.get("/eu/plaid/link_token")
def get_plaid_link_token_eu(
    db: Session = Depends(get_db),
    jwt = Depends(get_current_user),
    redirect_uri: Optional[str] = None,
    mode: Optional[str] = None,
    countries: Optional[str] = None,
):
    """Return a Plaid EU Link token.

    Query params:
      - mode: "auth" | "pi" (default: "pi")
      - countries: comma-separated ISO2 list (e.g., FR,IE)
    """
    user: Optional[User] = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        plaid_client = PlaidClient()
        cc_list = None
        if countries:
            req = [c.strip().upper() for c in countries.split(',') if c.strip()]
            # Intersect with allowed list
            cc_list = [c for c in req if c in _ALLOWED_EU_ISO2]
            if not cc_list:
                cc_list = _ALLOWED_EU_ISO2
        else:
            cc_list = _ALLOWED_EU_ISO2

        if (mode or '').lower() == 'auth':
            resp = plaid_client.create_eu_auth_link_token(str(user.id), country_codes=cc_list, redirect_uri=redirect_uri)
        else:
            resp = plaid_client.create_eu_link_token(str(user.id), country_codes=cc_list, redirect_uri=redirect_uri)
        return resp
    except requests.HTTPError as e:
        status = e.response.status_code if getattr(e, "response", None) else 502
        detail = e.response.text if getattr(e, "response", None) else str(e)
        raise HTTPException(status_code=status, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.post("/eu/plaid/exchange_auth")
def exchange_plaid_token_eu_auth(payload: PublicTokenSchema, db: Session = Depends(get_db), jwt = Depends(get_current_user)):
    """EU Auth flow: exchange public_token, call /auth/get and /identity/get, then create Bridge external account with IBAN/BIC.

    Identity matching is relaxed for sandbox; we prefer Plaid's owner name when available.
    """
    user: Optional[User] = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == user.id).first()
    if not bridge_customer:
        raise HTTPException(status_code=404, detail="Bridge customer not found")

    try:
        plaid = PlaidClient()
        ex = plaid.exchange_public_token(payload.public_token)
        access_token = ex.get("access_token")
        item_id = ex.get("item_id")
        auth = plaid.get_auth(access_token)
        identity = plaid.get_identity(access_token)
    except requests.HTTPError as e:
        status = e.response.status_code if getattr(e, "response", None) else 502
        detail = e.response.text if getattr(e, "response", None) else str(e)
        raise HTTPException(status_code=status, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    # Extract IBAN/BIC
    iban_entry = None
    try:
        for entry in (auth.get("numbers", {}) or {}).get("international", []) or []:
            iban_entry = entry
            break
    except Exception:
        iban_entry = None
    if not iban_entry:
        raise HTTPException(status_code=422, detail="Institution did not return IBAN via Auth; please enter IBAN manually.")

    # Collect owner names
    plaid_names: List[str] = []
    try:
        for account in identity.get("accounts", []) or []:
            for owner in account.get("owners", []) or []:
                plaid_names.extend(owner.get("names", []) or [])
    except Exception:
        plaid_names = []

    verified, _reason = verify_identity_advanced(
        bridge_customer.first_name or "",
        bridge_customer.last_name or "",
        plaid_names,
    )
    if not verified:
        raise HTTPException(status_code=400, detail="Identity verification failed")

    # Choose owner name (use BridgeCustomer, already verified)
    owner_full = f"{bridge_customer.first_name or ''} {bridge_customer.last_name or ''}".strip()
    try:
        owner_first = bridge_customer.first_name or ""
        owner_last = bridge_customer.last_name or ""
    except Exception:
        owner_first = bridge_customer.first_name or ""
        owner_last = bridge_customer.last_name or ""

    # Normalize country to ISO3 for Bridge
    try:
        country = _derive_iban_country(iban_entry)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"country_normalization_failed: {e}")

    try:
        bridge_payload = {
        "currency": "eur",
        "account_type": "iban",
        "bank_name": payload.institution_name or "EU Bank",
        "account_name": f"{payload.institution_name or 'EU Bank'} Account",
        "first_name": owner_first,
        "last_name": owner_last,
        "account_owner_type": "individual",
        "account_owner_name": owner_full or f"{owner_first} {owner_last}".strip() or "Unknown",
        "iban": {
            "account_number": iban_entry.get("iban"),
            "bic": iban_entry.get("bic"),
            "country": country,
        },
        "address": {
            "street_line_1": bridge_customer.street_line_1 or "",
            "city": bridge_customer.city or "",
            "state": bridge_customer.subdivision or "",
            "postal_code": bridge_customer.postal_code or "",
            "country": (bridge_customer.country or country or "").upper(),
        },
    }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"payload_build_failed: {e}")

    # Log masked payload for debugging (no sensitive values)
    try:
        masked = dict(bridge_payload)
        masked_iban = (bridge_payload.get("iban", {}) or {}).get("account_number", "")
        masked_bic = (bridge_payload.get("iban", {}) or {}).get("bic", "")
        if isinstance(masked.get("iban"), dict):
            masked["iban"] = {
                "account_number": f"****{masked_iban[-4:]}" if masked_iban else None,
                "bic": f"***{masked_bic[-3:]}" if masked_bic else None,
                "country": bridge_payload.get("iban", {}).get("country"),
            }
        logging.getLogger(__name__).info(
            "Creating Bridge EU external_account with payload (masked): %s",
            json.dumps(masked),
        )
    except Exception:
        pass

    # Persist Plaid item FIRST (peg external account to Plaid)
    from datetime import datetime
    try:
        item = PlaidItem(
            external_account_id=None,
            customer_id=bridge_customer.id,
            user_id=user.id,
            access_token=access_token,
            item_id=item_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(item)
        db.flush()  # Ensure plaid_item_id is generated
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"plaid_item_persist_failed: {e}")

    try:
        created = BridgeClient().create_external_account(bridge_customer.id, bridge_payload)
    except requests.HTTPError as e:
        # Log exact upstream error for debugging
        body_text = getattr(e, "response", None).text if getattr(e, "response", None) else str(e)
        try:
            logging.getLogger(__name__).error(
                "Bridge create_external_account failed: status=%s, body=%s",
                getattr(e, "response", None).status_code if getattr(e, "response", None) else None,
                body_text,
            )
        except Exception:
            pass

        # If duplicate external account, fetch and proceed with existing
        try:
            data = json.loads(body_text)
            if isinstance(data, dict) and data.get("code") == "duplicate_external_account" and data.get("id"):
                existing_id = data["id"]
                created = BridgeClient().get_external_account(existing_id, customer_id=bridge_customer.id)
            else:
                status = e.response.status_code if getattr(e, "response", None) else 502
                db.rollback()
                raise HTTPException(status_code=status, detail=body_text)
        except ValueError:
            # Not JSON; rethrow
            status = e.response.status_code if getattr(e, "response", None) else 502
            db.rollback()
            raise HTTPException(status_code=status, detail=body_text)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=502, detail=f"Failed to create Bridge external account: {e}")

    # Store ExternalAccount and link to Plaid item
    try:
        ext = ExternalAccount(
            external_account_id=created["id"],
            customer_id=bridge_customer.id,
            user_id=user.id,
            currency=created.get("currency", "eur"),
            bank_name=created.get("bank_name", payload.institution_name or "Bank"),
            account_owner_name=created.get("account_owner_name", owner_full),
            account_owner_type=created.get("account_owner_type", "individual"),
            last_4=(created.get("iban", {}) or {}).get("last_4") or (created.get("account", {}) or {}).get("last_4", ""),
            active=created.get("active", True),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            plaid_item_id=item.plaid_item_id,
        )
        db.add(ext)
        db.flush()

        # Backfill item.external_account_id for compatibility
        item.external_account_id = created["id"]
        item.updated_at = datetime.utcnow()
        db.add(item)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"local_persist_failed: {e}")

    return {"account_id": created["id"], "plaid_item_id": str(item.plaid_item_id)}
@router.get("/plaid/link_token")
def get_plaid_link_token(db: Session = Depends(get_db), jwt = Depends(get_current_user)):
    """Return OUR Plaid Link token for the authenticated user (Option A flow)."""
    user: Optional[User] = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get bridge customer from related table  
    bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == user.id).first()
    if not bridge_customer:
        raise HTTPException(status_code=404, detail="Bridge customer not found")

    try:
        # Use OUR Plaid credentials to create link token (Option A)
        plaid_client = PlaidClient()
        resp = plaid_client.create_link_token(
            user_id=str(user.id),
            webhook_url=None  # Add webhook URL if needed
        )
        return resp
    except Exception as e:
        raise HTTPException(status_code=502, detail="Failed to create Plaid Link token") from e

@router.post("/plaid/exchange/{link_token}")
def exchange_plaid_token(link_token: str, payload: PublicTokenSchema, db: Session = Depends(get_db), jwt = Depends(get_current_user)):
    """Option A: Exchange Plaid public_token with our credentials and manually create Bridge accounts."""
    
    # Ensure user exists (authorization)
    user: Optional[User] = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get bridge customer for operations
    bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == user.id).first()
    if not bridge_customer:
        raise HTTPException(status_code=404, detail="Bridge customer not found")

    # ------------------------------------------------------------------
    # Step 1: Exchange Plaid public token with OUR credentials
    # ------------------------------------------------------------------
    access_token = None
    item_id = None
    try:
        plaid_client = PlaidClient()
        plaid_resp = plaid_client.exchange_public_token(payload.public_token)
        access_token = plaid_resp.get("access_token")
        item_id = plaid_resp.get("item_id")
    except Exception as e:
        raise HTTPException(status_code=502, detail="Plaid token exchange failed") from e

    # ------------------------------------------------------------------
    # Step 2: Fetch Auth and Identity data from Plaid
    # ------------------------------------------------------------------
    try:
        plaid_auth = plaid_client.get_auth(access_token)
        plaid_identity = plaid_client.get_identity(access_token)
        accounts = plaid_auth.get("accounts", [])
        
        # Use the first account (the one the user selected in Plaid Link)
        selected_account = accounts[0]
        
    except Exception as e:
        raise HTTPException(status_code=502, detail="Failed to fetch account data from Plaid") from e

    # ------------------------------------------------------------------
    # Step 3: Perform advanced identity verification
    # ------------------------------------------------------------------
    
    # Extract all owner names from Plaid Identity
    plaid_names = []
    for account in plaid_identity.get("accounts", []):
        for owner in account.get("owners", []):
            plaid_names.extend(owner.get("names", []))
    
    # Perform advanced identity verification
    identity_verified, verification_reason = verify_identity_advanced(
        bridge_customer.first_name or "",
        bridge_customer.last_name or "",
        plaid_names
    )
    
    if not identity_verified:
        raise HTTPException(status_code=400, detail=f"Identity verification failed: {verification_reason}")

    # ------------------------------------------------------------------
    # Step 4: Persist Plaid item FIRST, then create Bridge external account
    # ------------------------------------------------------------------
    from datetime import datetime
    try:
        plaid_item = PlaidItem(
            external_account_id=None,
            customer_id=bridge_customer.id,
            user_id=user.id,
            access_token=access_token,
            item_id=item_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(plaid_item)
        db.flush()  # ensure plaid_item_id is generated
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"plaid_item_persist_failed: {e}")

    # Map to Bridge payload and create account (with duplicate handling)
    try:
        bridge_payload = map_plaid_to_bridge_external_account(
            plaid_auth, plaid_identity, bridge_customer, selected_account.get('account_id'), payload.institution_name
        )
        bridge_client = BridgeClient()
        try:
            bridge_account = bridge_client.create_external_account(bridge_customer.id, bridge_payload)
        except requests.HTTPError as e:
            body_text = getattr(e, "response", None).text if getattr(e, "response", None) else str(e)
            try:
                logging.getLogger(__name__).error(
                    "Bridge create_external_account (US) failed: status=%s, body=%s",
                    getattr(e, "response", None).status_code if getattr(e, "response", None) else None,
                    body_text,
                )
            except Exception:
                pass
            # Attempt duplicate recovery if Bridge returns duplicate_external_account
            try:
                data = json.loads(body_text)
                if isinstance(data, dict) and data.get("code") == "duplicate_external_account" and data.get("id"):
                    existing_id = data["id"]
                    bridge_account = bridge_client.get_external_account(existing_id, customer_id=bridge_customer.id)
                else:
                    db.rollback()
                    raise HTTPException(status_code=e.response.status_code if getattr(e, "response", None) else 502, detail=body_text)
            except ValueError:
                db.rollback()
                raise HTTPException(status_code=e.response.status_code if getattr(e, "response", None) else 502, detail=body_text)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=502, detail=f"Failed to create Bridge external account: {e}")

    # ------------------------------------------------------------------
    # Step 5: Store ExternalAccount and link to Plaid item
    # ------------------------------------------------------------------
    try:
        created_at = datetime.utcnow()
        updated_at = datetime.utcnow()
        if bridge_account.get("created_at"):
            try:
                created_at = datetime.fromisoformat(bridge_account["created_at"].replace("Z", "+00:00"))
            except:
                pass
        if bridge_account.get("updated_at"):
            try:
                updated_at = datetime.fromisoformat(bridge_account["updated_at"].replace("Z", "+00:00"))
            except:
                pass

        ext = ExternalAccount(
            external_account_id=bridge_account["id"],
            customer_id=bridge_customer.id,
            user_id=user.id,
            currency=bridge_account.get("currency", "usd"),
            bank_name=bridge_account.get("bank_name", payload.institution_name or "Bank"),
            account_owner_name=bridge_account.get("account_owner_name", f"{bridge_customer.first_name or ''} {bridge_customer.last_name or ''}".strip()),
            account_owner_type=bridge_account.get("account_owner_type", "individual"),
            business_name=bridge_account.get("business_name"),
            last_4=bridge_account.get("account", {}).get("last_4", "") if bridge_account.get("account") else "",
            active=bridge_account.get("active", False),
            created_at=created_at,
            updated_at=updated_at,
            plaid_item_id=plaid_item.plaid_item_id,
        )
        db.add(ext)
        db.flush()

        # Backfill PlaidItem.external_account_id for compatibility
        plaid_item.external_account_id = bridge_account["id"]
        plaid_item.updated_at = datetime.utcnow()
        db.add(plaid_item)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to store account locally: {e}") from e

    return {
        "message": "Successfully linked bank account via Option A flow",
        "account_id": bridge_account["id"],
        "account_count": 1,
        "institution_name": payload.institution_name
    }

# -------- List accounts --------

@router.get("/accounts")
def list_external_accounts(db: Session = Depends(get_db), jwt = Depends(get_current_user)):
    """Return all external accounts for the authenticated user from our local database."""
    user: Optional[User] = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get external accounts directly from our local database
    external_accounts = db.query(ExternalAccount).filter(ExternalAccount.user_id == user.id).all()
    
    # Map to frontend-friendly format
    mapped_accounts = []
    for acc in external_accounts:
        mapped_accounts.append({
            "id": acc.external_account_id,
            "bank_name": acc.bank_name,
            "last4": acc.last_4,
            "currency": acc.currency.upper() if acc.currency else "USD",
            "active": acc.active
        })
    
    return {"accounts": mapped_accounts}



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
        account_type = acc.get("account_type", "us")  # us, eu, etc.
        account_name = acc.get("account_name", f"{bank_name} Account")
        
        # Determine account subtype (checking, savings, etc.)
        checking_or_savings = acc.get("account", {}).get("checking_or_savings", "checking")

        ext = db.query(ExternalAccount).filter(ExternalAccount.external_account_id == acc["id"]).first()
        if not ext:
            ext = ExternalAccount(external_account_id=acc["id"], user_id=user.id)
            db.add(ext)
        ext.bank_name = bank_name
        ext.last_4 = last4
        ext.currency = currency
        
        # Active status from Bridge API
        active = acc.get("active", True)

        mapped.append({
            "id": acc["id"],
            "bank_name": bank_name,
            "account_name": account_name,
            "account_type": checking_or_savings.title(),  # "Checking", "Savings"
            "last4": last4,
            "masked_account": f"****{last4}" if last4 else None,
            "currency": currency.upper() if currency else "USD",
            "status": "Active" if active else "Inactive",
            "active": active,
            "payment_method_type": "bank_account",
            "display_name": f"{bank_name} {checking_or_savings.title()} ****{last4}" if last4 else f"{bank_name} Account"
        })
    db.commit()
    return mapped 



 

@router.get("/accounts/{account_id}")
def get_external_account_details(account_id: str, db: Session = Depends(get_db), jwt = Depends(get_current_user)):
    """Return details for a single external account from our local database."""
    # Authorize user
    user: Optional[User] = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get external account from our local database
    ext = db.query(ExternalAccount).filter(
        ExternalAccount.external_account_id == account_id, 
        ExternalAccount.user_id == user.id
    ).first()
    
    if not ext:
        raise HTTPException(status_code=404, detail="Account not found")

    return {
        "id": ext.external_account_id,
        "bank_name": ext.bank_name,
        "account_name": f"{ext.bank_name} Account",
        "account_type": "Checking",
        "last4": ext.last_4,
        "masked_account": f"****{ext.last_4}" if ext.last_4 else None,
        "currency": ext.currency.upper() if ext.currency else "USD",
        "status": "Active" if ext.active else "Inactive",
        "active": ext.active,
        "payment_method_type": "bank_account",
        "display_name": f"{ext.bank_name} ****{ext.last_4}" if ext.last_4 else f"{ext.bank_name} Account"
    }

# ---------------------------------------------------------------------------
# Delete external account                                                    
# ---------------------------------------------------------------------------

@router.delete("/accounts/{account_id}")
def delete_external_account(account_id: str, db: Session = Depends(get_db), jwt = Depends(get_current_user)):
    """Delete an external account both on Bridge and locally."""
    user: Optional[User] = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get bridge customer from related table
    bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == user.id).first()
    if not bridge_customer:
        raise HTTPException(status_code=404, detail="Bridge customer not found")

    # Verify ownership locally first
    ext = db.query(ExternalAccount).filter(ExternalAccount.external_account_id == account_id, ExternalAccount.user_id == user.id).first()
    if not ext:
        raise HTTPException(status_code=404, detail="Account not found")

    try:
        BridgeClient().delete_external_account(bridge_customer.id, account_id)
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
    user: Optional[User] = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ext = (
        db.query(ExternalAccount)
        .filter(ExternalAccount.external_account_id == account_id, ExternalAccount.user_id == user.id)
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