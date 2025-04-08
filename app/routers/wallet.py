from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Wallet, User
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
from app.dependencies.auth import get_current_user
from sqlalchemy import text

router = APIRouter()

class DepositRequest(BaseModel):
    user_id: int
    amount: float
    currency: str = "USD"  # Currency of the deposit

class WalletUpdate(BaseModel):
    user_id: int
    display_currency: str  # Only updating display currency

class WalletCreate(BaseModel):
    user_id: int
    base_currency: str
    country_code: Optional[str] = None
    display_currency: Optional[str] = None

class WalletUpdateFull(BaseModel):
    base_currency: Optional[str] = None
    display_currency: Optional[str] = None
    country_code: Optional[str] = None
    blockchain_address: Optional[str] = None
    currency_settings: Optional[Dict[str, Any]] = None

@router.post("/deposit/")
def deposit_fiat(deposit: DepositRequest, db: Session = Depends(get_db)):
    """
    Deposit fiat currency into a user's wallet.
    Each user has only one wallet by design, which primarily holds their local currency.
    If the deposit is in a currency different from the base currency, conversion is applied.
    """
    user_wallet = db.query(Wallet).filter(Wallet.user_id == deposit.user_id).first()
    if not user_wallet:
        # If wallet doesn't exist, create one with the currency of this deposit
        user_wallet = Wallet(
            user_id=deposit.user_id,
            fiat_balance=0,
            stablecoin_balance=0,
            base_currency=deposit.currency,
            display_currency=deposit.currency
        )
        db.add(user_wallet)
        db.commit()
        db.refresh(user_wallet)
    
    # Check if deposit currency matches the wallet's base currency
    if deposit.currency == user_wallet.base_currency:
        # Direct deposit, no conversion needed
        user_wallet.fiat_balance += deposit.amount
    else:
        # For demo/prototype, we'll use a simplified conversion
        # In production, this would use a real-time exchange rate service
        from app.utils.conversion import fetch_conversion_rate
        conversion_rate = fetch_conversion_rate(deposit.currency, user_wallet.base_currency)
        converted_amount = deposit.amount * conversion_rate
        user_wallet.fiat_balance += converted_amount
    
    db.commit()
    return {
        "message": "Fiat deposit successful",
        "new_balance": user_wallet.fiat_balance,
        "currency": user_wallet.base_currency,
        "display_currency": user_wallet.display_currency
    }

@router.get("/{user_id}")
def get_wallet(user_id: int, db: Session = Depends(get_db)):
    """
    Get a user's wallet details with balance in both base and display currencies.
    Each user has one wallet that stores their balances in their local currency.
    If the wallet doesn't exist, create a default one.
    """
    try:
        # Use raw SQL to avoid ORM issues
        wallet_query = """
            SELECT id, user_id, fiat_balance, stablecoin_balance, base_currency, 
                   display_currency, country_code, blockchain_address
            FROM wallets 
            WHERE user_id = :user_id
        """
        wallet_result = db.execute(text(wallet_query), {"user_id": user_id}).first()
        
        if not wallet_result:
            # Auto-create a wallet for the user if it doesn't exist
            create_wallet_query = """
                INSERT INTO wallets (user_id, fiat_balance, stablecoin_balance, base_currency, display_currency)
                VALUES (:user_id, 0, 0, 'USD', 'USD')
                RETURNING id, user_id, fiat_balance, stablecoin_balance, base_currency, display_currency, country_code, blockchain_address
            """
            wallet_result = db.execute(text(create_wallet_query), {"user_id": user_id}).first()
            db.commit()
        
        # Transform the SQL result into a dictionary
        wallet = {
            "id": wallet_result[0],
            "user_id": wallet_result[1],
            "fiat_balance": wallet_result[2],
            "stablecoin_balance": wallet_result[3],
            "base_currency": wallet_result[4],
            "display_currency": wallet_result[5],
            "country_code": wallet_result[6],
            "blockchain_address": wallet_result[7]
        }
        
        # Get display balance in the preferred display currency
        display_balance = wallet["fiat_balance"]
        
        # Only convert if necessary
        if wallet["base_currency"] != wallet["display_currency"]:
            # Convert the balance for display purposes
            from app.utils.conversion import fetch_conversion_rate
            try:
                conversion_rate = fetch_conversion_rate(wallet["base_currency"], wallet["display_currency"])
                display_balance = wallet["fiat_balance"] * conversion_rate
            except Exception as e:
                print(f"Error in conversion: {str(e)}")
        
        return {
            "id": wallet["id"],
            "user_id": wallet["user_id"],
            "fiat_balance": wallet["fiat_balance"],
            "base_currency": wallet["base_currency"],
            "display_balance": display_balance,
            "display_currency": wallet["display_currency"],
            "stablecoin_balance": wallet["stablecoin_balance"],
            "country_code": wallet["country_code"]
        }
    except Exception as e:
        print(f"Error getting wallet: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching wallet: {str(e)}")

@router.patch("/display-currency")
def update_display_currency(wallet_update: WalletUpdate, db: Session = Depends(get_db)):
    """
    Update a wallet's display currency preference.
    This doesn't change the actual stored value, just how it's presented to the user.
    """
    wallet = db.query(Wallet).filter(Wallet.user_id == wallet_update.user_id).first()
    if not wallet:
        # Auto-create a wallet with the requested display currency
        wallet = Wallet(
            user_id=wallet_update.user_id, 
            fiat_balance=0, 
            stablecoin_balance=0, 
            base_currency="USD",  # Default base currency
            display_currency=wallet_update.display_currency.upper()
        )
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
        return {
            "message": "Wallet created with display currency successfully",
            "wallet": {
                "id": wallet.id,
                "user_id": wallet.user_id,
                "fiat_balance": wallet.fiat_balance,
                "stablecoin_balance": wallet.stablecoin_balance,
                "base_currency": wallet.base_currency,
                "display_currency": wallet.display_currency
            }
        }
    
    # Validate currency code - in a real app, check against a list of supported currencies
    wallet.display_currency = wallet_update.display_currency.upper()
    db.commit()
    
    # Get display balance in the new preferred display currency
    display_balance = wallet.fiat_balance
    
    if wallet.base_currency != wallet.display_currency:
        # Convert the balance for display purposes
        from app.utils.conversion import fetch_conversion_rate
        conversion_rate = fetch_conversion_rate(wallet.base_currency, wallet.display_currency)
        display_balance = wallet.fiat_balance * conversion_rate
    
    return {
        "message": "Display currency updated successfully",
        "wallet": {
            "id": wallet.id,
            "user_id": wallet.user_id,
            "fiat_balance": wallet.fiat_balance,
            "base_currency": wallet.base_currency,
            "display_balance": display_balance,
            "display_currency": wallet.display_currency,
            "stablecoin_balance": wallet.stablecoin_balance
        }
    }

@router.put("/update/{user_id}")
def update_wallet_full(user_id: int, wallet_data: WalletUpdateFull, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    """
    Update a user's wallet with currency, country code, and other settings.
    This endpoint enables setting the wallet's base currency based on the user's country selection.
    """
    # Get current user ID for permission check
    current_user_data = db.execute(
        text("SELECT id, role FROM users WHERE username = :username"),
        {"username": current_user}
    ).first()
    
    if not current_user_data:
        raise HTTPException(status_code=404, detail="Current user not found")
    
    current_user_id, role = current_user_data
    
    # Only allow the wallet owner or admin to update the wallet
    if current_user_id != user_id and role != "admin":
        raise HTTPException(status_code=403, detail="You don't have permission to update this wallet")
    
    # Get the wallet
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    # Update fields if provided
    if wallet_data.base_currency:
        # If changing base currency, we need to handle conversion of the balance
        if wallet.base_currency != wallet_data.base_currency.upper():
            # Get current balance in the original currency
            original_balance = wallet.fiat_balance
            original_currency = wallet.base_currency
            
            # Get conversion rate to new currency
            from app.utils.conversion import fetch_conversion_rate
            conversion_rate = fetch_conversion_rate(original_currency, wallet_data.base_currency.upper())
            
            # Convert the balance to the new currency
            new_balance = original_balance * conversion_rate
            
            # Update the wallet with new currency and converted balance
            wallet.base_currency = wallet_data.base_currency.upper()
            wallet.fiat_balance = new_balance
        else:
            # Just update the currency code without conversion
            wallet.base_currency = wallet_data.base_currency.upper()
    
    # Update display currency if provided
    if wallet_data.display_currency:
        wallet.display_currency = wallet_data.display_currency.upper()
    
    # Update country code if provided
    if wallet_data.country_code:
        wallet.country_code = wallet_data.country_code
    
    # Update blockchain address if provided
    if wallet_data.blockchain_address:
        wallet.blockchain_address = wallet_data.blockchain_address
    
    # Update currency settings if provided
    if wallet_data.currency_settings:
        # If wallet has existing settings, merge them with new settings
        if wallet.currency_settings:
            current_settings = json.loads(wallet.currency_settings)
            current_settings.update(wallet_data.currency_settings)
            wallet.currency_settings = json.dumps(current_settings)
        else:
            wallet.currency_settings = json.dumps(wallet_data.currency_settings)
    
    db.commit()
    
    # Calculate display balance
    display_balance = wallet.fiat_balance
    if wallet.base_currency != wallet.display_currency:
        from app.utils.conversion import fetch_conversion_rate
        conversion_rate = fetch_conversion_rate(wallet.base_currency, wallet.display_currency)
        display_balance = wallet.fiat_balance * conversion_rate
    
    return {
        "message": "Wallet updated successfully",
        "wallet": {
            "id": wallet.id,
            "user_id": wallet.user_id,
            "fiat_balance": wallet.fiat_balance,
            "base_currency": wallet.base_currency,
            "display_balance": display_balance,
            "display_currency": wallet.display_currency,
            "stablecoin_balance": wallet.stablecoin_balance,
            "country_code": wallet.country_code,
            "blockchain_address": wallet.blockchain_address
        }
    }

@router.get("/lookup/{id_or_address}/")
def lookup_wallet(id_or_address: str, db: Session = Depends(get_db)):
    """
    Lookup a wallet by user ID, wallet ID, or blockchain address.
    Used when sending money to verify the recipient exists.
    Returns limited information for security reasons.
    """
    # Try to look up by ID
    if id_or_address.isdigit():
        user_id = int(id_or_address)
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
            if wallet:
                return {
                    "found": True,
                    "wallet_id": wallet.id,
                    "user_id": user.id,
                    "username": user.username,
                    "currency": wallet.base_currency,
                    "address": wallet.blockchain_address or "Not available"
                }
    
    # Try to look up by blockchain address
    wallet = db.query(Wallet).filter(Wallet.blockchain_address == id_or_address).first()
    if wallet:
        user = db.query(User).filter(User.id == wallet.user_id).first()
        return {
            "found": True, 
            "wallet_id": wallet.id,
            "user_id": user.id,
            "username": user.username,
            "currency": wallet.base_currency,
            "address": wallet.blockchain_address
        }
    
    # Not found
    raise HTTPException(status_code=404, detail="Wallet not found")

@router.get("/")
def get_all_wallets(db: Session = Depends(get_db)):
    """Get all wallets (admin function)"""
    wallets = db.query(Wallet).all()
    return wallets

@router.post("/create")
def create_wallet(wallet_data: WalletCreate, db: Session = Depends(get_db)):
    """
    Create a wallet for a user if they don't already have one.
    This enforces the one-wallet-per-user model.
    """
    # Check if user exists
    user = db.query(User).filter(User.id == wallet_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if the user already has a wallet
    existing_wallet = db.query(Wallet).filter(Wallet.user_id == wallet_data.user_id).first()
    if existing_wallet:
        # Return 409 Conflict to indicate that the resource already exists
        # This makes it clear to the client that multiple wallets per user are not allowed
        raise HTTPException(
            status_code=409, 
            detail="User already has a wallet. Each user can only have one wallet."
        )
    
    # Set display currency same as base if not specified
    display_currency = wallet_data.display_currency or wallet_data.base_currency
    
    # Create new wallet
    new_wallet = Wallet(
        user_id=wallet_data.user_id,
        fiat_balance=0,
        stablecoin_balance=0,
        base_currency=wallet_data.base_currency,
        display_currency=display_currency,
        country_code=wallet_data.country_code,
        currency_settings=json.dumps({
            "allowed_currencies": [wallet_data.base_currency, "USD", "EUR", "GBP"],
            "conversion_fee_percent": 1.0,  # 1% fee for currency conversions
            "regulatory_status": "compliant"
        })
    )
    
    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)
    
    return {
        "message": "Wallet created successfully",
        "wallet": {
            "id": new_wallet.id,
            "user_id": new_wallet.user_id,
            "fiat_balance": new_wallet.fiat_balance,
            "stablecoin_balance": new_wallet.stablecoin_balance,
            "base_currency": new_wallet.base_currency,
            "display_currency": new_wallet.display_currency,
            "country_code": new_wallet.country_code
        }
    }
