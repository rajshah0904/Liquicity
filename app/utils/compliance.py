from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from pydantic import BaseModel, EmailStr, validator
import re
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import User, Transaction, Wallet
from fastapi import HTTPException

class KYCStatus(str, Enum):
    """KYC verification status"""
    NOT_STARTED = "not_started"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_ADDITIONAL_INFO = "requires_additional_info"

class RiskLevel(str, Enum):
    """Risk level for users and transactions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

class VerificationType(str, Enum):
    """Types of verification methods"""
    DOCUMENT = "document"
    ADDRESS = "address"
    PHONE = "phone"
    EMAIL = "email"
    FACIAL = "facial"
    LIVENESS = "liveness"

class KYCRequest(BaseModel):
    """Data model for KYC verification request"""
    user_id: int
    full_name: str
    dob: str  # Date of birth in YYYY-MM-DD format
    address: str
    country: str
    id_type: str  # passport, driver_license, national_id
    id_number: str
    id_expiry: str  # YYYY-MM-DD format
    phone: str
    email: EmailStr
    selfie_image_url: Optional[str] = None
    document_front_url: Optional[str] = None
    document_back_url: Optional[str] = None
    
    @validator('dob', 'id_expiry')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')
        return v
        
    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^\+?[0-9]{8,15}$', v):
            raise ValueError('Invalid phone number format')
        return v

class AMLCheckResult(BaseModel):
    """Results of AML screening"""
    user_id: int
    timestamp: datetime = datetime.now()
    passed: bool
    risk_level: RiskLevel = RiskLevel.LOW
    check_reference_id: str
    flags: List[str] = []
    details: Dict[str, Any] = {}

class TransactionRiskAssessment(BaseModel):
    """Risk assessment for a transaction"""
    transaction_id: int
    timestamp: datetime = datetime.now()
    risk_level: RiskLevel = RiskLevel.LOW
    approved: bool = True
    flags: List[str] = []
    details: Dict[str, Any] = {}

class ComplianceService:
    """
    Service for KYC verification and AML compliance
    
    In a production environment, this would integrate with:
    - ID verification services (Jumio, Onfido, etc.)
    - AML screening providers (ComplyAdvantage, Trulioo, etc.)
    - Sanctions lists (OFAC, UN, EU, etc.)
    - Transaction monitoring systems
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    def start_kyc_verification(self, request: KYCRequest) -> Dict[str, Any]:
        """
        Initiate KYC verification process for a user
        
        Args:
            request: KYC verification request data
            
        Returns:
            Verification status and reference
        """
        # Get user from database
        user = self.db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # In a real implementation, you would:
        # 1. Call an external KYC provider API
        # 2. Store verification documents securely
        # 3. Track verification status
        
        # Mock implementation - would be replaced with actual API calls
        verification_status = KYCStatus.PENDING
        verification_id = f"KYC-{request.user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Store KYC status in user metadata (in a real system, use a dedicated table)
        user_metadata = {
            "kyc_status": verification_status,
            "kyc_reference": verification_id,
            "kyc_timestamp": datetime.now().isoformat(),
            "kyc_details": {
                "name": request.full_name,
                "country": request.country,
                "id_type": request.id_type
            }
        }
        
        # In a real implementation, update user with metadata
        # user.metadata = json.dumps(user_metadata)
        # self.db.commit()
        
        return {
            "status": verification_status,
            "reference": verification_id,
            "user_id": request.user_id,
            "timestamp": datetime.now().isoformat(),
            "estimated_completion_time": (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
    def check_kyc_status(self, user_id: int) -> Dict[str, Any]:
        """
        Check the KYC verification status for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Current KYC status and details
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # In a real implementation, fetch from user metadata or dedicated KYC table
        # For this mock, we'll assume a random status
        import random
        statuses = list(KYCStatus)
        mock_status = random.choice(statuses)
        
        return {
            "user_id": user_id,
            "status": mock_status,
            "reference": f"KYC-{user_id}-MOCKREF",
            "last_updated": datetime.now().isoformat(),
            "details": {
                "verified_fields": ["email", "phone"] if mock_status == KYCStatus.APPROVED else [],
                "pending_fields": [] if mock_status == KYCStatus.APPROVED else ["document", "address"],
                "rejection_reason": "Documents unclear" if mock_status == KYCStatus.REJECTED else None
            }
        }
        
    def screen_user_aml(self, user_id: int) -> AMLCheckResult:
        """
        Perform AML screening on a user
        
        Args:
            user_id: User ID to screen
            
        Returns:
            AML screening result
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # In a real implementation, call AML screening API
        # For this mock, we'll assume a random result
        import random
        risk_levels = list(RiskLevel)
        mock_risk = random.choice(risk_levels)
        passed = mock_risk in [RiskLevel.LOW, RiskLevel.MEDIUM]
        
        result = AMLCheckResult(
            user_id=user_id,
            passed=passed,
            risk_level=mock_risk,
            check_reference_id=f"AML-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            flags=["PEP"] if mock_risk == RiskLevel.HIGH else [],
            details={
                "check_provider": "MockAML",
                "sanctions_checked": ["UN", "OFAC", "EU"],
                "match_details": {
                    "is_match": mock_risk in [RiskLevel.HIGH, RiskLevel.EXTREME],
                    "match_type": "name" if mock_risk == RiskLevel.HIGH else None,
                    "match_score": 0.85 if mock_risk == RiskLevel.HIGH else 0.1
                }
            }
        )
        
        return result
        
    def assess_transaction_risk(self, transaction_id: int) -> TransactionRiskAssessment:
        """
        Assess the risk of a transaction
        
        Args:
            transaction_id: Transaction ID to assess
            
        Returns:
            Transaction risk assessment
        """
        transaction = self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
            
        # Get sender and recipient
        sender = self.db.query(User).filter(User.id == transaction.sender_id).first()
        recipient = self.db.query(User).filter(User.id == transaction.recipient_id).first()
        
        # In a real implementation, analyze:
        # 1. Transaction amount (higher amounts = higher risk)
        # 2. Sender and recipient countries (high-risk jurisdictions)
        # 3. Transaction frequency and patterns
        # 4. User risk levels
        
        # Simple logic for demo:
        # - High-value transactions are higher risk
        # - Cryptocurrency transactions are higher risk
        # - Cross-currency transactions are higher risk
        
        flags = []
        risk_level = RiskLevel.LOW
        
        # Check amount threshold (e.g., >$10,000 is high risk)
        if transaction.source_amount > 10000:
            flags.append("high_value_transaction")
            risk_level = RiskLevel.MEDIUM
            
        # Check if crypto transaction
        if transaction.source_currency in ["USDT", "USDC", "BTC", "ETH"]:
            flags.append("cryptocurrency_transaction")
            risk_level = max(risk_level, RiskLevel.MEDIUM)
            
        # Check cross-currency
        if transaction.source_currency != transaction.target_currency:
            flags.append("cross_currency_transaction")
            
        # Check if first-time transaction
        sender_previous_txs = self.db.query(Transaction).filter(
            Transaction.sender_id == transaction.sender_id
        ).count()
        
        if sender_previous_txs <= 1:  # Including this one
            flags.append("new_sender")
            risk_level = max(risk_level, RiskLevel.MEDIUM)
            
        # Check for rapid, repetitive transactions
        recent_txs = self.db.query(Transaction).filter(
            Transaction.sender_id == transaction.sender_id,
            Transaction.timestamp >= datetime.now() - timedelta(hours=24)
        ).count()
        
        if recent_txs > 5:
            flags.append("frequent_transactions")
            risk_level = max(risk_level, RiskLevel.HIGH)
            
        # Final decision
        approved = risk_level != RiskLevel.EXTREME
        
        assessment = TransactionRiskAssessment(
            transaction_id=transaction_id,
            risk_level=risk_level,
            approved=approved,
            flags=flags,
            details={
                "sender_id": transaction.sender_id,
                "recipient_id": transaction.recipient_id,
                "amount": transaction.source_amount,
                "currency": transaction.source_currency,
                "target_currency": transaction.target_currency,
                "transaction_time": transaction.timestamp.isoformat() if transaction.timestamp else None,
                "risk_factors": {
                    "high_value": transaction.source_amount > 10000,
                    "cross_currency": transaction.source_currency != transaction.target_currency,
                    "is_crypto": transaction.source_currency in ["USDT", "USDC", "BTC", "ETH"],
                    "new_sender": sender_previous_txs <= 1,
                    "high_frequency": recent_txs > 5
                }
            }
        )
        
        return assessment

# Create a function to get the compliance service
def get_compliance_service(db: Session) -> ComplianceService:
    """Get a compliance service instance"""
    return ComplianceService(db) 