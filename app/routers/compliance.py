from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.compliance import (
    get_compliance_service, 
    ComplianceService, 
    KYCRequest, 
    KYCStatus, 
    AMLCheckResult,
    TransactionRiskAssessment
)
from app.dependencies.auth import get_current_user
from typing import Dict, List, Any
from pydantic import BaseModel

router = APIRouter()

class KYCStatusResponse(BaseModel):
    """Response model for KYC status"""
    user_id: int
    status: KYCStatus
    reference: str
    last_updated: str
    details: Dict[str, Any]

@router.post("/kyc/verify")
def start_kyc_verification(
    request: KYCRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Start KYC verification process for a user"""
    compliance_service = get_compliance_service(db)
    return compliance_service.start_kyc_verification(request)

@router.get("/kyc/status/{user_id}", response_model=KYCStatusResponse)
def check_kyc_status(
    user_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Check the KYC verification status for a user"""
    compliance_service = get_compliance_service(db)
    return compliance_service.check_kyc_status(user_id)

@router.post("/aml/screen/{user_id}", response_model=AMLCheckResult)
def screen_user_aml(
    user_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Perform AML screening on a user"""
    compliance_service = get_compliance_service(db)
    return compliance_service.screen_user_aml(user_id)

@router.post("/transaction/assess/{transaction_id}", response_model=TransactionRiskAssessment)
def assess_transaction_risk(
    transaction_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Assess the risk of a transaction"""
    compliance_service = get_compliance_service(db)
    return compliance_service.assess_transaction_risk(transaction_id)

# Webhook endpoint for external verification services
class VerificationWebhook(BaseModel):
    """Webhook payload from verification provider"""
    reference_id: str
    status: str
    timestamp: str
    verification_type: str
    result: Dict[str, Any]

@router.post("/webhook/verification")
def verification_webhook(
    webhook: VerificationWebhook,
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for external verification providers
    
    This would be called by services like Jumio, Onfido, etc. when
    verification processes are completed.
    """
    # In a real implementation, you would:
    # 1. Verify the webhook signature
    # 2. Parse the result and update user verification status
    # 3. Trigger appropriate notifications
    
    # Mock response
    return {
        "received": True,
        "reference_id": webhook.reference_id,
        "status": webhook.status,
        "processing": "queued"
    } 