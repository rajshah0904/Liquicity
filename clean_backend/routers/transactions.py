from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import logging

from ..database import get_db
from ..auth import get_current_user
from ..models import User, Transaction, Dispute, ComplianceReport, BlacklistedAddress
from ..services.walletconnect_service import WalletConnectV2Service, WalletConnectError
from ..services.security import security_validator
from ..config.settings import ERROR_CODES

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/transactions", tags=["transactions"])

# Pydantic models
class TransactionResponse(BaseModel):
    id: str
    user_id: str
    from_wallet: str
    to_wallet: str
    amount: float
    currency: str
    chain_type: str
    status: str
    tx_hash: Optional[str] = None
    risk_score: float
    flagged: bool
    notes: Optional[str] = None
    created_at: datetime
    confirmed_at: Optional[datetime] = None

class TransactionHistoryResponse(BaseModel):
    transactions: List[TransactionResponse]
    total: int
    page: int
    per_page: int

class DisputeRequest(BaseModel):
    transaction_id: str
    reason: str

class DisputeResponse(BaseModel):
    id: str
    transaction_id: str
    user_id: str
    reason: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

class ComplianceReportResponse(BaseModel):
    id: str
    transaction_id: Optional[str] = None
    user_id: Optional[str] = None
    report_type: str
    details: Optional[str] = None
    created_at: datetime
    reviewed: bool
    reviewed_at: Optional[datetime] = None

class BlacklistAddressRequest(BaseModel):
    address: str
    chain_type: str
    reason: str

class BlacklistAddressResponse(BaseModel):
    id: int
    address: str
    chain_type: str
    reason: str
    created_at: datetime
    active: bool

# Dependency to get WalletConnect service
async def get_walletconnect_service():
    from ..database import get_settings
    settings = get_settings()
    return WalletConnectV2Service(settings, security_validator, ERROR_CODES)

# Transaction History Endpoint
@router.get("/history", response_model=TransactionHistoryResponse)
async def get_transaction_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    chain_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Get paginated transaction history for the authenticated user"""
    user_obj = db.query(User).filter(User.auth0_id == user.get("sub")).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = db.query(Transaction).filter(Transaction.user_id == user_obj.id)
    
    if status:
        query = query.filter(Transaction.status == status)
    if chain_type:
        query = query.filter(Transaction.chain_type == chain_type)
    
    total = query.count()
    transactions = query.order_by(Transaction.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    
    return TransactionHistoryResponse(
        transactions=[TransactionResponse.from_orm(tx) for tx in transactions],
        total=total,
        page=page,
        per_page=per_page
    )

# Transaction Status Polling Endpoint
@router.get("/{transaction_id}/status")
async def get_transaction_status(
    transaction_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
    service: WalletConnectV2Service = Depends(get_walletconnect_service)
):
    """Get real-time transaction status with blockchain confirmation"""
    user_obj = db.query(User).filter(User.auth0_id == user.get("sub")).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == user_obj.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # If transaction has a hash, check blockchain status
    if transaction.tx_hash and transaction.status == "pending":
        try:
            # Check blockchain for confirmation
            confirmed = await service.check_transaction_confirmation(
                transaction.tx_hash, 
                transaction.chain_type
            )
            if confirmed:
                transaction.status = "confirmed"
                transaction.confirmed_at = datetime.utcnow()
                db.commit()
        except Exception as e:
            logger.error(f"Error checking transaction confirmation: {e}")
    
    return TransactionResponse.from_orm(transaction)

# Create Dispute Endpoint
@router.post("/dispute", response_model=DisputeResponse)
async def create_dispute(
    request: DisputeRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Create a dispute for a transaction"""
    user_obj = db.query(User).filter(User.auth0_id == user.get("sub")).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify transaction belongs to user
    transaction = db.query(Transaction).filter(
        Transaction.id == request.transaction_id,
        Transaction.user_id == user_obj.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Check if dispute already exists
    existing_dispute = db.query(Dispute).filter(
        Dispute.transaction_id == request.transaction_id,
        Dispute.user_id == user_obj.id
    ).first()
    
    if existing_dispute:
        raise HTTPException(status_code=400, detail="Dispute already exists for this transaction")
    
    dispute = Dispute(
        transaction_id=request.transaction_id,
        user_id=user_obj.id,
        reason=request.reason,
        status="open"
    )
    
    db.add(dispute)
    db.commit()
    db.refresh(dispute)
    
    return DisputeResponse.from_orm(dispute)

# Get User Disputes Endpoint
@router.get("/disputes", response_model=List[DisputeResponse])
async def get_user_disputes(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Get all disputes for the authenticated user"""
    user_obj = db.query(User).filter(User.auth0_id == user.get("sub")).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    
    disputes = db.query(Dispute).filter(Dispute.user_id == user_obj.id).all()
    return [DisputeResponse.from_orm(dispute) for dispute in disputes]

# Admin Endpoints (require admin role)
async def get_admin_user(user: dict = Depends(get_current_user)):
    """Verify user has admin privileges"""
    # TODO: Implement proper admin role checking
    # For now, allow all authenticated users
    return user

# Admin: Get All Transactions
@router.get("/admin/all", response_model=List[TransactionResponse])
async def get_all_transactions(
    status: Optional[str] = Query(None),
    flagged: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    """Admin endpoint to get all transactions with filtering"""
    query = db.query(Transaction)
    
    if status:
        query = query.filter(Transaction.status == status)
    if flagged is not None:
        query = query.filter(Transaction.flagged == flagged)
    
    transactions = query.order_by(Transaction.created_at.desc()).limit(100).all()
    return [TransactionResponse.from_orm(tx) for tx in transactions]

# Admin: Get All Disputes
@router.get("/admin/disputes", response_model=List[DisputeResponse])
async def get_all_disputes(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    """Admin endpoint to get all disputes"""
    query = db.query(Dispute)
    
    if status:
        query = query.filter(Dispute.status == status)
    
    disputes = query.order_by(Dispute.created_at.desc()).all()
    return [DisputeResponse.from_orm(dispute) for dispute in disputes]

# Admin: Resolve Dispute
@router.put("/admin/disputes/{dispute_id}/resolve")
async def resolve_dispute(
    dispute_id: str,
    resolution: str = Query(..., description="Resolution: 'resolved' or 'rejected'"),
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    """Admin endpoint to resolve a dispute"""
    dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
    
    if resolution not in ["resolved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid resolution")
    
    dispute.status = resolution
    dispute.resolved_at = datetime.utcnow()
    db.commit()
    
    return {"success": True, "message": f"Dispute {resolution}"}

# Admin: Blacklist Management
@router.post("/admin/blacklist", response_model=BlacklistAddressResponse)
async def add_blacklisted_address(
    request: BlacklistAddressRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    """Admin endpoint to add an address to the blacklist"""
    # Check if address already exists
    existing = db.query(BlacklistedAddress).filter(
        BlacklistedAddress.address == request.address,
        BlacklistedAddress.chain_type == request.chain_type
    ).first()
    
    if existing:
        existing.active = True
        existing.reason = request.reason
        db.commit()
        return BlacklistAddressResponse.from_orm(existing)
    
    blacklisted = BlacklistedAddress(
        address=request.address,
        chain_type=request.chain_type,
        reason=request.reason,
        active=True
    )
    
    db.add(blacklisted)
    db.commit()
    db.refresh(blacklisted)
    
    return BlacklistAddressResponse.from_orm(blacklisted)

@router.get("/admin/blacklist", response_model=List[BlacklistAddressResponse])
async def get_blacklisted_addresses(
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    """Admin endpoint to get all blacklisted addresses"""
    query = db.query(BlacklistedAddress)
    
    if active_only:
        query = query.filter(BlacklistedAddress.active == True)
    
    addresses = query.order_by(BlacklistedAddress.created_at.desc()).all()
    return [BlacklistAddressResponse.from_orm(addr) for addr in addresses]

@router.put("/admin/blacklist/{address_id}/deactivate")
async def deactivate_blacklisted_address(
    address_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    """Admin endpoint to deactivate a blacklisted address"""
    address = db.query(BlacklistedAddress).filter(BlacklistedAddress.id == address_id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Blacklisted address not found")
    
    address.active = False
    db.commit()
    
    return {"success": True, "message": "Address deactivated"}

# Compliance Reporting Endpoints
@router.get("/admin/compliance", response_model=List[ComplianceReportResponse])
async def get_compliance_reports(
    report_type: Optional[str] = Query(None),
    reviewed: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    """Admin endpoint to get compliance reports"""
    query = db.query(ComplianceReport)
    
    if report_type:
        query = query.filter(ComplianceReport.report_type == report_type)
    if reviewed is not None:
        query = query.filter(ComplianceReport.reviewed == reviewed)
    
    reports = query.order_by(ComplianceReport.created_at.desc()).all()
    return [ComplianceReportResponse.from_orm(report) for report in reports]

@router.put("/admin/compliance/{report_id}/review")
async def review_compliance_report(
    report_id: str,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    """Admin endpoint to mark a compliance report as reviewed"""
    report = db.query(ComplianceReport).filter(ComplianceReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Compliance report not found")
    
    report.reviewed = True
    report.reviewed_at = datetime.utcnow()
    db.commit()
    
    return {"success": True, "message": "Report marked as reviewed"} 