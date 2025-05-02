from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models import User, Transaction, Wallet
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from app.payments.services.orchestrator import transfer_cross_border
from app.payments.services.payment_service import receive_fiat, send_fiat

router = APIRouter()

class DepositRequest(BaseModel):
    user_id: int
    amount: float
    currency: str
    payment_method: str = "bank_transfer"  # bank_transfer, card, crypto
    payment_details: Optional[Dict[str, Any]] = None
    
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

class WithdrawalRequest(BaseModel):
    user_id: int
    amount: float
    currency: str
    withdrawal_method: str = "bank_transfer"
    withdrawal_details: Optional[Dict[str, Any]] = None
    
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

class TransferRequest(BaseModel):
    sender_id: int
    recipient_id: int
    amount: float
    source_currency: str
    target_currency: str = None
    description: str = ""
    use_stablecoin: bool = True
    skip_sender_deduction: bool = False
    payment_source: str = "wallet"
    transaction_type: str = "TRANSFER"
    
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

class TransferCrossBorderRequest(BaseModel):
    amount: float
    src_cc: str  # Source country code
    dst_cc: str  # Destination country code
    currency: str
    chain: str = "polygon"
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v
        
    @validator('src_cc', 'dst_cc')
    def validate_country_code(cls, v):
        if len(v) != 2 or not v.isalpha():
            raise ValueError('Country code must be a 2-letter ISO code')
        return v

@router.post("/deposit")
async def process_deposit(
    request: DepositRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Process a deposit to a user's wallet"""
    # Get user wallet
    wallet = db.query(Wallet).filter(Wallet.user_id == request.user_id).first()
    
    # Auto-create wallet if it doesn't exist
    if not wallet:
        wallet = Wallet(
            user_id=request.user_id,
            fiat_balance=0,
            stablecoin_balance=0,
            base_currency=request.currency,
            display_currency=request.currency
        )
        db.add(wallet)
        db.commit()
        db.refresh(wallet)

    # Process deposit via the payment service
    payment_result = await receive_fiat(
        request.user_id, 
        request.amount, 
        request.currency,
        payment_details=request.payment_details
    )

    # Update wallet balance
    wallet.fiat_balance += request.amount

    # Record the deposit as a transaction
    transaction = Transaction(
        sender_id=request.user_id,  # Self-deposit
        recipient_id=request.user_id,
        source_amount=request.amount,
        source_currency=request.currency,
        target_amount=request.amount,
        target_currency=wallet.base_currency,
        status="completed"
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(wallet)
    db.refresh(transaction)
    
    return {
        "success": True,
        "deposit_id": transaction.id,
        "payment_id": payment_result.transaction_id if payment_result else None,
        "amount": request.amount,
        "currency": request.currency,
        "new_balance": wallet.fiat_balance,
        "wallet_currency": wallet.base_currency
    }

@router.post("/withdraw")
async def process_withdrawal(
    request: WithdrawalRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Process a withdrawal from a user's wallet"""
    # Get user wallet
    wallet = db.query(Wallet).filter(Wallet.user_id == request.user_id).first()
    
    if not wallet:
        raise HTTPException(status_code=404, detail="User wallet not found")

    # Check sufficient funds
    if wallet.fiat_balance < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Process withdrawal via the payment service
    payment_result = await send_fiat(
        request.user_id, 
        request.amount, 
        request.currency,
        withdrawal_details=request.withdrawal_details
    )

    # Update wallet balance
    wallet.fiat_balance -= request.amount

    # Record transaction
    transaction = Transaction(
        sender_id=request.user_id,
        recipient_id=request.user_id,  # Self-withdrawal
        source_amount=request.amount,
        source_currency=wallet.base_currency,
        target_amount=request.amount,
        target_currency=request.currency,
        status="completed"
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(wallet)
    db.refresh(transaction)
    
    return {
        "success": True,
        "withdrawal_id": transaction.id,
        "payment_id": payment_result.transaction_id if payment_result else None,
        "amount": request.amount,
        "currency": request.currency,
        "new_balance": wallet.fiat_balance,
        "wallet_currency": wallet.base_currency
    }

@router.post("/transfer")
def process_transfer(
    request: TransferRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Process a transfer between users, handling currency conversion"""
    # Verify current user is allowed to make this transfer
    user = db.query(User).filter(User.username == username).first()
    if not user or (user.id != request.sender_id and not user.is_admin):
        raise HTTPException(status_code=403, detail="Not authorized to make transfers from this account")
    
    # Prevent sending money to yourself
    if request.sender_id == request.recipient_id:
        raise HTTPException(status_code=400, detail="Cannot send money to yourself")
    
    try:
        # Get sender wallet
        sender_wallet = db.query(Wallet).filter(Wallet.user_id == request.sender_id).first()
        if not sender_wallet:
            raise HTTPException(status_code=404, detail="Sender wallet not found")
            
        # Get recipient wallet
        recipient_wallet = db.query(Wallet).filter(Wallet.user_id == request.recipient_id).first()
        if not recipient_wallet:
            # Create recipient wallet if it doesn't exist
            recipient_wallet = Wallet(
                user_id=request.recipient_id,
                fiat_balance=0,
                stablecoin_balance=0,
                base_currency=request.target_currency or request.source_currency,
                display_currency=request.target_currency or request.source_currency
            )
            db.add(recipient_wallet)
            db.commit()
            db.refresh(recipient_wallet)
        
        # Check sufficient funds (if not skipping sender deduction)
        if not request.skip_sender_deduction and sender_wallet.fiat_balance < request.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
            
        # Deduct from sender (if not skipping)
        if not request.skip_sender_deduction:
            sender_wallet.fiat_balance -= request.amount
            
        # Add to recipient
        recipient_wallet.fiat_balance += request.amount
        
        # Create transaction record
        transaction = Transaction(
            sender_id=request.sender_id,
            recipient_id=request.recipient_id,
            source_amount=request.amount,
            source_currency=request.source_currency,
            target_amount=request.amount,
            target_currency=request.target_currency or request.source_currency,
            status="completed",
            transaction_type=request.transaction_type,
            description=request.description
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        return {
            "success": True,
            "transaction_id": transaction.id,
            "amount": request.amount,
            "currency": request.source_currency,
            "target_currency": request.target_currency or request.source_currency,
            "sender_balance": sender_wallet.fiat_balance if not request.skip_sender_deduction else None,
            "recipient_balance": recipient_wallet.fiat_balance
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Transfer failed: {str(e)}")

@router.post("/payments/transfer")
async def cross_border_transfer(
    req: TransferCrossBorderRequest, 
    user: User = Depends(get_current_user)
):
    """
    Execute a cross-border transfer using stablecoins as an intermediary.
    
    This endpoint orchestrates the complete flow:
    1. Pull funds from user's local payment source
    2. Mint USDC with the fiat amount
    3. Transfer on-chain (handled internally by Circle)
    4. Redeem USDC to destination fiat
    5. Pay out to the recipient
    """
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
        
    try:
        steps = await transfer_cross_border(
            user.id, 
            req.amount, 
            req.src_cc, 
            req.dst_cc, 
            req.currency,
            req.chain,
            req.metadata
        )
        
        if steps["status"] != "completed":
            # Handle various error states
            if steps["status"] == "refunded":
                return {
                    "success": False,
                    "status": "refunded",
                    "message": "Transfer failed but funds were refunded",
                    "steps": steps
                }
            else:
                return {
                    "success": False,
                    "status": steps["status"],
                    "message": "Transfer encountered an issue",
                    "steps": steps
                }
        
        return {
            "success": True,
            "status": "completed",
            "steps": steps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cross-border transfer failed: {str(e)}")
