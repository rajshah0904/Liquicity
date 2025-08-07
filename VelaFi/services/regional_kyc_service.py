import logging
from typing import Any, Dict, Literal, Optional

from sqlalchemy.orm import Session

from clean_backend.bridge import BridgeClient
from VelaFi.services.velafi_kyc_service import VelafiKycService
from VelaFi.velafi_client import VelafiClient

_log = logging.getLogger(__name__)


# Regional KYC configuration
REGIONAL_KYC_CONFIG = {
    "bridge_regions": {
        "US": "bridge", "CA": "bridge", "GB": "bridge", "DE": "bridge", "FR": "bridge", 
        "IT": "bridge", "ES": "bridge", "NL": "bridge", "SE": "bridge", "CH": "bridge", 
        "AT": "bridge", "BE": "bridge", "DK": "bridge", "FI": "bridge", "IE": "bridge", 
        "NO": "bridge", "PT": "bridge", "PL": "bridge", "CZ": "bridge", "HU": "bridge", 
        "RO": "bridge", "BG": "bridge", "HR": "bridge", "SI": "bridge", "SK": "bridge", 
        "LT": "bridge", "LV": "bridge", "EE": "bridge", "MT": "bridge", "CY": "bridge", 
        "LU": "bridge", "IS": "bridge", "LI": "bridge", "MC": "bridge", "SM": "bridge", 
        "VA": "bridge", "AD": "bridge",
    },
    "velafi_regions": {
        "MX": "velafi", "BR": "velafi", "AR": "velafi", "CL": "velafi", "CO": "velafi", 
        "PE": "velafi", "VE": "velafi", "EC": "velafi", "BO": "velafi", "PY": "velafi", 
        "UY": "velafi", "GY": "velafi", "SR": "velafi", "GF": "velafi", "FK": "velafi", 
        "CR": "velafi", "PA": "velafi", "NI": "velafi", "HN": "velafi", "GT": "velafi", 
        "BZ": "velafi", "SV": "velafi", "CU": "velafi", "JM": "velafi", "HT": "velafi", 
        "DO": "velafi", "PR": "velafi", "TT": "velafi", "BB": "velafi", "GD": "velafi", 
        "LC": "velafi", "VC": "velafi", "AG": "velafi", "KN": "velafi", "DM": "velafi", 
        "BS": "velafi", "AI": "velafi", "VG": "velafi", "VI": "velafi", "AW": "velafi", 
        "CW": "velafi", "SX": "velafi", "TC": "velafi", "KY": "velafi", "BM": "velafi", 
        "MS": "velafi", "GP": "velafi", "MQ": "velafi", "BL": "velafi", "MF": "velafi", 
        "GL": "velafi",
    }
}


class RegionalKycService:
    """Service for determining and managing KYC based on user's region."""
    
    def __init__(self, velafi_client: VelafiClient):
        self.velafi_client = velafi_client
        self.velafi_kyc_service = VelafiKycService(velafi_client)
        self.bridge_client = BridgeClient()
    
    def get_kyc_system_for_country(self, country_code: str) -> Literal["bridge", "velafi"]:
        """Determine which KYC system to use based on country code."""
        country_code = country_code.upper()
        
        if country_code in REGIONAL_KYC_CONFIG["bridge_regions"]:
            return "bridge"
        elif country_code in REGIONAL_KYC_CONFIG["velafi_regions"]:
            return "velafi"
        else:
            # Default to Bridge for unsupported countries
            _log.warning(f"Country {country_code} not in regional config, defaulting to Bridge KYC")
            return "bridge"
    
    def get_kyc_requirements(self, country_code: str) -> Dict[str, Any]:
        """Get KYC requirements for a specific country."""
        kyc_system = self.get_kyc_system_for_country(country_code)
        
        if kyc_system == "bridge":
            return {
                "system": "bridge",
                "type": "hosted_link",
                "required_fields": ["first_name", "last_name", "email", "date_of_birth", "address"],
                "required_documents": ["government_id", "proof_of_address"],
                "description": "Bridge hosted KYC flow for US/EU compliance"
            }
        else:  # velafi
            return {
                "system": "velafi",
                "type": "direct_api",
                "required_fields": ["first_name", "last_name", "email", "date_of_birth", "phone", "address", "city", "state", "postal_code"],
                "required_documents": ["national_id", "proof_of_address"],
                "description": "VelaFi direct KYC for LATAM compliance",
                "country_specific": {
                    "MX": {"id_type": "INE", "tax_id": "RFC"},
                    "BR": {"id_type": "CPF", "tax_id": "CPF"},
                    "AR": {"id_type": "DNI", "tax_id": "CUIT"},
                    "CL": {"id_type": "RUT", "tax_id": "RUT"},
                    "CO": {"id_type": "CC", "tax_id": "NIT"},
                    "PE": {"id_type": "DNI", "tax_id": "RUC"},
                }
            }
    
    async def check_kyc_status(self, db: Session, user_id: str, country_code: str) -> Dict[str, Any]:
        """Check KYC status for a user based on their country."""
        kyc_system = self.get_kyc_system_for_country(country_code)
        
        if kyc_system == "bridge":
            return await self._check_bridge_kyc_status(db, user_id)
        else:  # velafi
            return await self._check_velafi_kyc_status(db, user_id)
    
    async def is_kyc_approved(self, db: Session, user_id: str, country_code: str) -> bool:
        """Check if user's KYC is approved for their country."""
        kyc_system = self.get_kyc_system_for_country(country_code)
        
        if kyc_system == "bridge":
            return await self._is_bridge_kyc_approved(db, user_id)
        else:  # velafi
            return await self._is_velafi_kyc_approved(db, user_id)
    
    def get_supported_countries(self) -> Dict[str, Dict[str, Any]]:
        """Get list of supported countries and their KYC systems."""
        return {
            "bridge_regions": REGIONAL_KYC_CONFIG["bridge_regions"],
            "velafi_regions": REGIONAL_KYC_CONFIG["velafi_regions"]
        }
    
    # Private methods for checking specific KYC systems
    
    async def _check_bridge_kyc_status(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Check Bridge KYC status."""
        from clean_backend.models import User
        
        user = db.query(User).filter(User.auth0_id == user_id).first()
        if not user:
            return {"status": "not_found", "system": "bridge"}
        
        return {
            "status": user.kyc_status or "pending",
            "system": "bridge",
            "customer_id": user.bridge_customer_id,
            "kyc_link_id": user.kyc_link_id,
            "kyc_url": user.kyc_url
        }
    
    async def _check_velafi_kyc_status(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Check VelaFi KYC status."""
        try:
            customer = await self.velafi_kyc_service.get_customer(db, user_id)
            if not customer:
                return {"status": "not_found", "system": "velafi"}
            
            # Get fresh status from VelaFi
            status_response = await self.velafi_kyc_service.get_kyc_status(db, user_id)
            
            return {
                "status": customer.kyc_status,
                "system": "velafi",
                "customer_id": customer.velafi_customer_id,
                "submitted_at": customer.kyc_submitted_at,
                "verified_at": customer.kyc_verified_at,
                "velafi_status": status_response
            }
        except Exception as e:
            _log.error(f"Error checking VelaFi KYC status for user {user_id}: {e}")
            return {"status": "error", "system": "velafi", "error": str(e)}
    
    async def _is_bridge_kyc_approved(self, db: Session, user_id: str) -> bool:
        """Check if Bridge KYC is approved."""
        from clean_backend.models import User
        
        user = db.query(User).filter(User.auth0_id == user_id).first()
        return user and user.kyc_status == "approved"
    
    async def _is_velafi_kyc_approved(self, db: Session, user_id: str) -> bool:
        """Check if VelaFi KYC is approved."""
        return await self.velafi_kyc_service.is_kyc_approved(db, user_id) 