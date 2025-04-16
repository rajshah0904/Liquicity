from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models import User, Transaction, Wallet
from app.utils.payment_processor import get_payment_processor
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
import re
from datetime import datetime, timedelta

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
    stripe_payment: bool = False
    skip_sender_deduction: bool = False
    payment_source: str = "wallet"
    transaction_type: str = "TRANSFER"
    
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

class CryptoTransferRequest(BaseModel):
    sender_id: int
    recipient_id: int
    amount: float
    crypto_currency: str = "USDT"
    description: str = ""
    
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v
        
    @validator('crypto_currency')
    def must_be_supported_crypto(cls, v):
        supported = ["USDT", "USDC", "BUSD", "DAI"]
        if v not in supported:
            raise ValueError(f"Unsupported cryptocurrency. Must be one of: {', '.join(supported)}")
        return v

class OnChainTransactionRequest(BaseModel):
    user_id: int
    blockchain_wallet_id: int
    recipient_address: str
    token_address: str
    amount: float
    private_key: str  # In production, never transmit private keys directly!
    gas_price_gwei: Optional[int] = None
    
    @validator('recipient_address')
    def validate_eth_address(cls, v):
        if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
            raise ValueError('Invalid Ethereum address format')
        return v
        
    @validator('token_address')
    def validate_token_address(cls, v):
        if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
            raise ValueError('Invalid token contract address format')
        return v

@router.post("/deposit")
def process_deposit(
    request: DepositRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Process a deposit to a user's wallet"""
    payment_processor = get_payment_processor(db)
    return payment_processor.process_deposit(
        user_id=request.user_id,
        amount=request.amount,
        currency=request.currency,
        payment_method=request.payment_method,
        payment_details=request.payment_details
    )

@router.post("/withdraw")
def process_withdrawal(
    request: WithdrawalRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Process a withdrawal from a user's wallet"""
    payment_processor = get_payment_processor(db)
    return payment_processor.process_withdrawal(
        user_id=request.user_id,
        amount=request.amount,
        currency=request.currency,
        withdrawal_method=request.withdrawal_method,
        withdrawal_details=request.withdrawal_details
    )

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
    
    # Prevent sending money to yourself with Stripe payments
    if request.sender_id == request.recipient_id and request.stripe_payment:
        raise HTTPException(status_code=400, detail="Cannot send money to yourself using a card payment")
    
    payment_processor = get_payment_processor(db)
    
    try:
        # Process the transfer
        result = payment_processor.process_transfer(
            sender_id=request.sender_id,
            recipient_id=request.recipient_id,
            amount=request.amount,
            source_currency=request.source_currency,
            target_currency=request.target_currency,
            description=request.description,
            use_stablecoin=request.use_stablecoin,
            stripe_payment=request.stripe_payment,
            skip_sender_deduction=request.skip_sender_deduction,
            payment_source=request.payment_source,
            transaction_type=request.transaction_type
        )
        
        # For Stripe payments, immediately check for and fix any self-deposits
        # This handles the issue where sender gets incorrectly credited when using Stripe
        if request.stripe_payment and request.sender_id != request.recipient_id:
            # Find any self-deposits created for the sender in the last minute
            sender_deposits = db.query(Transaction).filter(
                Transaction.sender_id == request.sender_id,
                Transaction.recipient_id == request.sender_id,
                Transaction.source_amount == request.amount,
                Transaction.source_currency == request.source_currency,
                Transaction.status == "completed",
                Transaction.timestamp >= datetime.utcnow() - timedelta(minutes=1)
            ).all()
            
            # If any incorrect self-deposits are found, void them and adjust balance
            for deposit in sender_deposits:
                print(f"Found incorrect self-deposit: ID={deposit.id}, Amount={deposit.source_amount}")
                
                # Get the sender's wallet
                sender_wallet = db.query(Wallet).filter(Wallet.user_id == request.sender_id).first()
                if sender_wallet:
                    # Adjust the balance by removing the duplicate amount
                    original_balance = sender_wallet.fiat_balance
                    sender_wallet.fiat_balance = max(0, original_balance - deposit.source_amount)
                    
                    # Mark the deposit as voided
                    deposit.status = "voided"
                    
                    print(f"Fixed balance: {original_balance} -> {sender_wallet.fiat_balance}")
                    print(f"Marked transaction #{deposit.id} as voided")
            
            # Commit changes if any deposits were fixed
            if sender_deposits:
                db.commit()
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process transfer: {str(e)}")

@router.post("/crypto/transfer")
def process_crypto_transfer(
    request: CryptoTransferRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Process a direct cryptocurrency transfer between users"""
    payment_processor = get_payment_processor(db)
    return payment_processor.process_crypto_transfer(
        sender_id=request.sender_id,
        recipient_id=request.recipient_id,
        amount=request.amount,
        crypto_currency=request.crypto_currency,
        description=request.description
    )

@router.post("/blockchain/transfer")
def process_on_chain_transaction(
    request: OnChainTransactionRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Process an on-chain token transfer (e.g., sending USDT on Ethereum)"""
    payment_processor = get_payment_processor(db)
    return payment_processor.process_on_chain_transaction(
        user_id=request.user_id,
        blockchain_wallet_id=request.blockchain_wallet_id,
        recipient_address=request.recipient_address,
        token_address=request.token_address,
        amount=request.amount,
        private_key=request.private_key,
        gas_price_gwei=request.gas_price_gwei
    )
