from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.payment_processor import get_payment_processor, PaymentProcessor
from app.dependencies.auth import get_current_user
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, validator
import re

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
    target_currency: Optional[str] = None
    description: str = ""
    use_stablecoin: bool = True
    
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v
        
    @validator('sender_id', 'recipient_id')
    def ids_must_be_different(cls, v, values):
        if 'sender_id' in values and values['sender_id'] == v and v == values.get('recipient_id'):
            raise ValueError('Sender and recipient must be different')
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
    payment_processor = get_payment_processor(db)
    return payment_processor.process_transfer(
        sender_id=request.sender_id,
        recipient_id=request.recipient_id,
        amount=request.amount,
        source_currency=request.source_currency,
        target_currency=request.target_currency,
        description=request.description,
        use_stablecoin=request.use_stablecoin
    )

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
