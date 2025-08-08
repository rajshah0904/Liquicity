from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user
from ..models import User, BridgeCustomer, BridgeWallet
from ..bridge import BridgeClient
from typing import Dict, Any
from decimal import Decimal

router = APIRouter(prefix="/wallet", tags=["wallet"])

def calculate_fiat_balance(bridge_wallet: BridgeWallet) -> Decimal:
    """Calculate total balance from fiat_balance_by_rate buckets
    
    New format: {"amount": rate} where keys are amounts and values are rates
    We sum the keys (amounts) to get total balance
    """
    if not bridge_wallet.fiat_balance_by_rate:
        return Decimal('0')
    
    total = Decimal('0')
    for amount_key, rate_value in bridge_wallet.fiat_balance_by_rate.items():
        # Sum the amounts (keys), not the rates (values)
        if isinstance(amount_key, (int, float, str)):
            try:
                total += Decimal(str(amount_key))
            except (ValueError, TypeError):
                # Skip invalid amount keys
                continue
    
    return total

@router.get("")
async def get_bridge_wallet(db: Session = Depends(get_db), jwt=Depends(get_current_user)):
    user = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get bridge customer and wallet from related tables
    bridge_customer = db.query(BridgeCustomer).filter(BridgeCustomer.user_id == user.id).first()
    if not bridge_customer:
        raise HTTPException(status_code=404, detail="Bridge customer not found")
    
    bridge_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == user.id).first()
    if not bridge_wallet:
        raise HTTPException(status_code=404, detail="Bridge wallet not found")
    
    try:
        wallet = BridgeClient().get_wallet(bridge_customer.id, bridge_wallet.wallet_id)
        
        # Add calculated balance from fiat_balance_by_rate
        calculated_balance = calculate_fiat_balance(bridge_wallet)
        wallet['fiat_balance'] = float(calculated_balance)
        wallet['fiat_currency'] = bridge_wallet.fiat_currency or 'USD'
        wallet['fiat_balance_by_rate'] = bridge_wallet.fiat_balance_by_rate
        
    except Exception as e:
        raise HTTPException(status_code=502, detail="Bridge unreachable") from e
    return wallet

@router.get("/overview")
async def get_wallet_overview(db: Session = Depends(get_db), jwt=Depends(get_current_user)):
    """Get wallet overview with calculated fiat balance"""
    user = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    bridge_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == user.id).first()
    if not bridge_wallet:
        raise HTTPException(status_code=404, detail="Bridge wallet not found")
    
    # Calculate balance from fiat_balance_by_rate
    total_balance = calculate_fiat_balance(bridge_wallet)
    
    return {
        "wallets": [{
            "id": bridge_wallet.wallet_id,
            "total_balance": float(total_balance),
            "available_balance": float(total_balance),  # For now, same as total
            "local_currency": bridge_wallet.fiat_currency or 'USD',
            "fiat_balance_by_rate": bridge_wallet.fiat_balance_by_rate
        }]
    }

@router.get("/history")
async def wallet_history(db: Session = Depends(get_db), jwt=Depends(get_current_user)):
    user = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    bridge_wallet = db.query(BridgeWallet).filter(BridgeWallet.user_id == user.id).first()
    if not bridge_wallet:
        raise HTTPException(status_code=404, detail="Bridge wallet not found")
    
    try:
        history = BridgeClient().get_wallet_history(bridge_wallet.wallet_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail="Bridge unreachable") from e
    return history 