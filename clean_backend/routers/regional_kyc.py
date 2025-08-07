import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from clean_backend.auth import get_current_user
from clean_backend.database import get_db
from VelaFi.services.regional_kyc_service import RegionalKycService
from VelaFi.velafi_client import VelafiClient

_log = logging.getLogger(__name__)

router = APIRouter(prefix="/kyc", tags=["Regional KYC"])


class KycRequirementsResponse(BaseModel):
    system: str
    type: str
    required_fields: list
    required_documents: list
    description: str
    country_specific: Dict[str, Any] = None


class KycStatusResponse(BaseModel):
    status: str
    system: str
    customer_id: str = None
    kyc_url: str = None
    submitted_at: str = None
    verified_at: str = None


def get_regional_kyc_service() -> RegionalKycService:
    velafi_client = VelafiClient()
    return RegionalKycService(velafi_client)


@router.get("/requirements/{country_code}", response_model=KycRequirementsResponse)
async def get_kyc_requirements(
    country_code: str,
    kyc_service: RegionalKycService = Depends(get_regional_kyc_service)
):
    """Get KYC requirements for a specific country."""
    try:
        requirements = kyc_service.get_kyc_requirements(country_code.upper())
        return KycRequirementsResponse(**requirements)
    except Exception as e:
        _log.error(f"Failed to get KYC requirements for country {country_code}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get KYC requirements: {str(e)}")


@router.get("/status", response_model=KycStatusResponse)
async def get_kyc_status(
    country_code: str,
    db: Session = Depends(get_db),
    jwt: dict = Depends(get_current_user),
    kyc_service: RegionalKycService = Depends(get_regional_kyc_service)
):
    """Get KYC status for the current user based on their country."""
    user_id = jwt.get("sub")
    
    try:
        status = await kyc_service.check_kyc_status(db, user_id, country_code.upper())
        return KycStatusResponse(**status)
    except Exception as e:
        _log.error(f"Failed to get KYC status for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get KYC status: {str(e)}")


@router.get("/approved")
async def check_kyc_approved(
    country_code: str,
    db: Session = Depends(get_db),
    jwt: dict = Depends(get_current_user),
    kyc_service: RegionalKycService = Depends(get_regional_kyc_service)
):
    """Check if KYC is approved for the current user based on their country."""
    user_id = jwt.get("sub")
    
    try:
        is_approved = await kyc_service.is_kyc_approved(db, user_id, country_code.upper())
        return {"approved": is_approved, "country": country_code.upper()}
    except Exception as e:
        _log.error(f"Failed to check KYC approval for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check KYC approval: {str(e)}")


@router.get("/supported-countries")
async def get_supported_countries(
    kyc_service: RegionalKycService = Depends(get_regional_kyc_service)
):
    """Get list of supported countries and their KYC systems."""
    try:
        countries = kyc_service.get_supported_countries()
        return {"countries": countries}
    except Exception as e:
        _log.error(f"Failed to get supported countries: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get supported countries: {str(e)}")


@router.get("/system/{country_code}")
async def get_kyc_system(
    country_code: str,
    kyc_service: RegionalKycService = Depends(get_regional_kyc_service)
):
    """Get the KYC system for a specific country."""
    try:
        system = kyc_service.get_kyc_system_for_country(country_code.upper())
        return {"country": country_code.upper(), "kyc_system": system}
    except Exception as e:
        _log.error(f"Failed to get KYC system for country {country_code}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get KYC system: {str(e)}") 