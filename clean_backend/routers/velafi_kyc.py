import logging
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from clean_backend.auth import get_current_user
from clean_backend.database import get_db
from VelaFi.services.velafi_kyc_service import VelafiKycService
from VelaFi.velafi_client import VelafiClient

_log = logging.getLogger(__name__)

router = APIRouter(prefix="/velafi/kyc", tags=["VelaFi KYC"])


class CustomerCreateRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    date_of_birth: str
    country: str
    phone: str
    address: str
    city: str
    state: str
    postal_code: str


class CustomerResponse(BaseModel):
    id: str
    velafi_customer_id: str
    first_name: str
    last_name: str
    email: str
    country: str
    kyc_status: str
    created_at: str


def get_velafi_kyc_service() -> VelafiKycService:
    velafi_client = VelafiClient()
    return VelafiKycService(velafi_client)


@router.post("/customer", response_model=CustomerResponse)
async def create_customer(
    request: CustomerCreateRequest,
    db: Session = Depends(get_db),
    jwt: dict = Depends(get_current_user),
    kyc_service: VelafiKycService = Depends(get_velafi_kyc_service)
):
    """Create a VelaFi customer for KYC purposes."""
    user_id = jwt.get("sub")
    
    try:
        customer_data = request.dict()
        customer = await kyc_service.create_customer(db, user_id, customer_data)
        
        return CustomerResponse(
            id=str(customer.id),
            velafi_customer_id=customer.velafi_customer_id,
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            country=customer.country,
            kyc_status=customer.kyc_status,
            created_at=customer.created_at.isoformat()
        )
    except Exception as e:
        _log.error(f"Failed to create VelaFi customer for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create customer: {str(e)}")


@router.get("/customer", response_model=CustomerResponse)
async def get_customer(
    db: Session = Depends(get_db),
    jwt: dict = Depends(get_current_user),
    kyc_service: VelafiKycService = Depends(get_velafi_kyc_service)
):
    """Get VelaFi customer information for the current user."""
    user_id = jwt.get("sub")
    
    customer = await kyc_service.get_customer(db, user_id)
    if not customer:
        raise HTTPException(status_code=404, detail="VelaFi customer not found")
    
    return CustomerResponse(
        id=str(customer.id),
        velafi_customer_id=customer.velafi_customer_id,
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email,
        country=customer.country,
        kyc_status=customer.kyc_status,
        created_at=customer.created_at.isoformat()
    )


@router.post("/documents")
async def upload_document(
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    jwt: dict = Depends(get_current_user),
    kyc_service: VelafiKycService = Depends(get_velafi_kyc_service)
):
    """Upload a KYC document."""
    user_id = jwt.get("sub")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_data = await file.read()
    if len(file_data) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    
    if len(file_data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    try:
        document = await kyc_service.upload_document(
            db, user_id, document_type, file_data, file.filename, file.content_type
        )
        
        return {
            "id": str(document.id),
            "velafi_document_id": document.velafi_document_id,
            "document_type": document.document_type,
            "filename": document.filename,
            "status": document.status
        }
    except Exception as e:
        _log.error(f"Failed to upload document for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")


@router.get("/approved")
async def check_kyc_approved(
    db: Session = Depends(get_db),
    jwt: dict = Depends(get_current_user),
    kyc_service: VelafiKycService = Depends(get_velafi_kyc_service)
):
    """Check if KYC is approved."""
    user_id = jwt.get("sub")
    
    try:
        is_approved = await kyc_service.is_kyc_approved(db, user_id)
        return {"approved": is_approved}
    except Exception as e:
        _log.error(f"Failed to check KYC approval for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check KYC approval: {str(e)}") 