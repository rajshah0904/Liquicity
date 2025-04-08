import os
import stripe
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models import User, BankAccount, Wallet, Transaction
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
import json
from datetime import datetime

router = APIRouter()

# Initialize Stripe with API key from environment variable
stripe.api_key = os.getenv("STRIPE_API_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
APP_URL = os.getenv("APP_URL", "http://localhost:3000")

# Check if API key is set
if not stripe.api_key:
    print("WARNING: Stripe API key is not set. Stripe endpoints will not work.")

# Models
class CheckoutSessionRequest(BaseModel):
    amount: int  # in cents
    currency: str
    type: str  # 'deposit' or 'payment'
    metadata: dict = {}

class BankAccountLinkRequest(BaseModel):
    user_id: int
    return_url: str
    cancel_url: str

class WithdrawalRequest(BaseModel):
    amount: int  # in cents
    currency: str
    bank_account_id: str
    user_id: int
    
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

class BankDepositRequest(BaseModel):
    amount: int  # in cents
    currency: str
    bank_account_id: str
    user_id: int
    
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

# Helper functions
def get_or_create_customer(db: Session, user_id: int) -> str:
    """Get or create a Stripe customer for the user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.stripe_customer_id:
        return user.stripe_customer_id
    
    # Create new customer
    customer = stripe.Customer.create(
        email=user.email,
        name=f"{user.first_name} {user.last_name}" if user.first_name else user.username,
        metadata={"user_id": user.id}
    )
    
    # Update user record
    user.stripe_customer_id = customer.id
    db.commit()
    
    return customer.id

def record_bank_account(db: Session, user_id: int, stripe_bank_account_id: str, bank_data: Dict) -> BankAccount:
    """Record a linked bank account in the database"""
    # Check if bank account already exists
    existing = db.query(BankAccount).filter(
        BankAccount.stripe_bank_id == stripe_bank_account_id,
        BankAccount.user_id == user_id
    ).first()
    
    if existing:
        # Update existing record
        existing.status = bank_data.get("status", "active")
        existing.last_updated = datetime.now()
        db.commit()
        return existing
    
    # Create new bank account record
    bank_account = BankAccount(
        user_id=user_id,
        stripe_bank_id=stripe_bank_account_id,
        bank_name=bank_data.get("bank_name", "Bank Account"),
        account_type=bank_data.get("account_type", "checking"),
        last4=bank_data.get("last4", ""),
        country=bank_data.get("country", "US"),
        currency=bank_data.get("currency", "usd"),
        status=bank_data.get("status", "active"),
        metadata=json.dumps(bank_data)
    )
    
    db.add(bank_account)
    db.commit()
    db.refresh(bank_account)
    
    return bank_account

def update_wallet_balance(db: Session, user_id: int, amount: float, currency: str, transaction_type: str):
    """Update user wallet balance"""
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    
    if not wallet:
        # Create wallet if it doesn't exist
        wallet = Wallet(
            user_id=user_id,
            fiat_balance=amount if transaction_type == "deposit" else 0,
            base_currency=currency.upper(),
            display_currency=currency.upper()
        )
        db.add(wallet)
    else:
        # Update existing wallet
        if transaction_type == "deposit":
            wallet.fiat_balance += amount
        elif transaction_type == "withdrawal":
            wallet.fiat_balance -= amount
    
    db.commit()
    
    # Record transaction
    transaction = Transaction(
        sender_id=user_id,
        recipient_id=user_id,  # Self-transaction for deposits/withdrawals
        stablecoin_amount=amount,
        source_amount=amount,
        source_currency=currency.upper(),
        target_amount=amount,
        target_currency=currency.upper(),
        source_to_stablecoin_rate=1.0,
        stablecoin_to_target_rate=1.0,
        status="completed"
    )
    
    db.add(transaction)
    db.commit()

# Routes
@router.post("/create-checkout")
async def create_checkout_session(
    request: CheckoutSessionRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Create a Stripe checkout session for deposit or payment"""
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get or create customer
        customer_id = get_or_create_customer(db, user.id)
        
        # Add user data to metadata
        metadata = request.metadata.copy()
        metadata.update({
            "user_id": str(user.id),
            "username": username,
            "type": request.type
        })
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            mode="payment",
            success_url=f"{APP_URL}/wallet?payment_success=true",
            cancel_url=f"{APP_URL}/wallet?payment_canceled=true",
            line_items=[{
                "price_data": {
                    "currency": request.currency.lower(),
                    "product_data": {
                        "name": f"{request.type.capitalize()} to TerraFlow Wallet",
                        "description": "Funds will be available immediately after payment"
                    },
                    "unit_amount": request.amount  # amount in cents
                },
                "quantity": 1
            }],
            metadata=metadata
        )
        
        # Update wallet immediately for development
        # In production this would be handled by webhook
        amount_dollars = request.amount / 100.0  # Convert cents to dollars
        update_wallet_balance(
            db=db,
            user_id=user.id,
            amount=amount_dollars,
            currency=request.currency.upper(),
            transaction_type="deposit"
        )
        
        return {"url": session.url, "session_id": session.id}
    
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/link-bank-account")
async def create_bank_account_link(
    request: BankAccountLinkRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Create a bank account link session for a user"""
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get or create customer
        customer_id = get_or_create_customer(db, user.id)
        
        # Create a bank account link
        link_account_session = stripe.financial_connections.Session.create(
            account_holder={
                "type": "customer",
                "customer": customer_id
            },
            permissions=["payment_method", "balances"],
            filters={"countries": ["US"]},
            return_url=request.return_url,
            refresh_url=request.cancel_url
        )
        
        return {
            "url": link_account_session.client_secret,
            "session_id": link_account_session.id
        }
    
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bank-accounts/{user_id}")
async def get_bank_accounts(
    user_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Get all bank accounts for a user"""
    try:
        # Check if authorized
        current_user = db.query(User).filter(User.username == username).first()
        if not current_user or (current_user.id != user_id and not current_user.is_admin):
            raise HTTPException(status_code=403, detail="Not authorized to access these bank accounts")
        
        # Get customer ID
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user.stripe_customer_id:
            return []
        
        # Get bank accounts from database
        bank_accounts = db.query(BankAccount).filter(
            BankAccount.user_id == user_id,
            BankAccount.status == "active"
        ).all()
        
        # Format response
        result = []
        for account in bank_accounts:
            result.append({
                "id": account.id,
                "stripe_bank_id": account.stripe_bank_id,
                "bank_name": account.bank_name,
                "account_type": account.account_type,
                "last4": account.last4,
                "country": account.country,
                "currency": account.currency
            })
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bank-deposit")
async def process_bank_deposit(
    request: BankDepositRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Process a direct deposit from a linked bank account"""
    try:
        # Check permissions
        user = db.query(User).filter(User.username == username).first()
        if not user or (user.id != request.user_id and not user.is_admin):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Get bank account
        bank_account = db.query(BankAccount).filter(
            BankAccount.id == request.bank_account_id,
            BankAccount.user_id == request.user_id
        ).first()
        
        if not bank_account:
            raise HTTPException(status_code=404, detail="Bank account not found")
        
        # Create ACH payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=request.amount,
            currency=request.currency.lower(),
            payment_method_types=["us_bank_account"],
            customer=user.stripe_customer_id,
            metadata={
                "user_id": str(request.user_id),
                "bank_account_id": str(request.bank_account_id),
                "transaction_type": "deposit"
            }
        )
        
        # Update wallet (normally would happen after webhook confirmation)
        # For demo purposes, we'll update it immediately
        amount_dollars = request.amount / 100.0  # Convert cents to dollars
        update_wallet_balance(
            db=db,
            user_id=request.user_id,
            amount=amount_dollars,
            currency=request.currency.upper(),
            transaction_type="deposit"
        )
        
        return {
            "success": True,
            "payment_intent_id": payment_intent.id,
            "status": payment_intent.status,
            "amount": amount_dollars,
            "currency": request.currency.upper()
        }
    
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/withdraw")
async def process_withdrawal(
    request: WithdrawalRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Process a withdrawal to a linked bank account"""
    try:
        # Check permissions
        user = db.query(User).filter(User.username == username).first()
        if not user or (user.id != request.user_id and not user.is_admin):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Get bank account
        bank_account = db.query(BankAccount).filter(
            BankAccount.id == request.bank_account_id,
            BankAccount.user_id == request.user_id
        ).first()
        
        if not bank_account:
            raise HTTPException(status_code=404, detail="Bank account not found")
        
        # Check wallet balance
        wallet = db.query(Wallet).filter(Wallet.user_id == request.user_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        amount_dollars = request.amount / 100.0  # Convert cents to dollars
        if wallet.fiat_balance < amount_dollars:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        
        # In a real implementation, you would:
        # 1. Create a payout to the user's bank account using Stripe Connect
        # 2. Update the wallet balance after the payout is confirmed
        
        # For demo purposes, we'll simulate a successful payout
        update_wallet_balance(
            db=db,
            user_id=request.user_id,
            amount=amount_dollars,
            currency=request.currency.upper(),
            transaction_type="withdrawal"
        )
        
        return {
            "success": True,
            "amount": amount_dollars,
            "currency": request.currency.upper(),
            "bank_account": f"{bank_account.bank_name} •••• {bank_account.last4}",
            "status": "processing",
            "estimated_arrival": "1-3 business days"
        }
    
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Handle Stripe webhook events"""
    try:
        # Get the signature from headers
        signature = request.headers.get("stripe-signature")
        if not signature:
            raise HTTPException(status_code=400, detail="Missing Stripe signature")
        
        # Get the raw body
        body = await request.body()
        
        # Verify signature
        try:
            event = stripe.Webhook.construct_event(
                payload=body,
                sig_header=signature,
                secret=STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Handle different event types
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            
            # Process completed checkout
            metadata = session.get("metadata", {})
            user_id = metadata.get("user_id")
            transaction_type = metadata.get("type", "deposit")
            
            if user_id:
                # Update wallet balance
                amount_cents = session.get("amount_total", 0)
                amount_dollars = amount_cents / 100.0
                currency = session.get("currency", "usd")
                
                # Update in background to avoid blocking webhook response
                background_tasks.add_task(
                    update_wallet_balance,
                    db=db,
                    user_id=int(user_id),
                    amount=amount_dollars,
                    currency=currency.upper(),
                    transaction_type=transaction_type
                )
        
        elif event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            
            # Process successful payment intent
            metadata = payment_intent.get("metadata", {})
            user_id = metadata.get("user_id")
            transaction_type = metadata.get("transaction_type", "payment")
            
            if user_id:
                # Update wallet balance
                amount_cents = payment_intent.get("amount", 0)
                amount_dollars = amount_cents / 100.0
                currency = payment_intent.get("currency", "usd")
                
                # Update in background
                background_tasks.add_task(
                    update_wallet_balance,
                    db=db,
                    user_id=int(user_id),
                    amount=amount_dollars,
                    currency=currency.upper(),
                    transaction_type=transaction_type
                )
        
        # Handle financial connections session completion
        elif event["type"] == "financial_connections.account.created":
            account = event["data"]["object"]
            
            # Get customer ID
            account_holder = account.get("account_holder", {})
            customer_id = account_holder.get("customer", None)
            
            if customer_id:
                # Find user with this customer ID
                user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
                
                if user:
                    # Record the bank account
                    bank_data = {
                        "bank_name": account.get("institution", {}).get("name", "Bank Account"),
                        "last4": account.get("last4", ""),
                        "account_type": account.get("category", "checking"),
                        "country": account.get("country", "US"),
                        "currency": account.get("currency", "usd"),
                        "status": "active"
                    }
                    
                    background_tasks.add_task(
                        record_bank_account,
                        db=db,
                        user_id=user.id,
                        stripe_bank_account_id=account.id,
                        bank_data=bank_data
                    )
        
        return {"status": "success"}
    
    except Exception as e:
        # Log the error but return 200 to acknowledge receipt
        print(f"Error processing webhook: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.get("/health")
async def health_check():
    """Check if Stripe is properly configured"""
    try:
        # Make a simple API call to test the key
        if not stripe.api_key:
            return {"status": "error", "message": "Stripe API key is not set"}
            
        # Try to list a customer to verify API key is valid
        stripe.Customer.list(limit=1)
        return {"status": "ok", "message": "Stripe API is properly configured"}
    except stripe.error.AuthenticationError:
        return {"status": "error", "message": "Invalid Stripe API key"}
    except Exception as e:
        return {"status": "error", "message": str(e)} 