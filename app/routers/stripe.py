import os
import stripe
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models import User, BankAccount, Wallet, Transaction
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
import json
from datetime import datetime
import uuid

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
    type: str  # 'deposit' or 'payment' or 'setup'
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

class DirectPaymentRequest(BaseModel):
    transaction: Dict[str, Any]  # Transaction data
    payment_method_id: str  # Stripe payment method ID
    payment_source: str  # 'card', 'bank', or 'wallet_partial'

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

# Routes
@router.post("/create-checkout")
async def create_checkout_session(
    request: CheckoutSessionRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Create a Stripe checkout session for deposit or payment"""
    print(f"CREATE CHECKOUT REQUEST: {request}")
    print(f"Stripe API Key: {stripe.api_key[:5]}...{stripe.api_key[-4:] if len(stripe.api_key) > 10 else ''}")
    
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"User not found: {username}")
            raise HTTPException(status_code=404, detail="User not found")
        
        print(f"User found: {user.id} ({user.username})")
        
        # Get or create customer
        customer_id = get_or_create_customer(db, user.id)
        print(f"Using Stripe customer ID: {customer_id}")
        
        # Add user data to metadata
        metadata = request.metadata.copy()
        metadata.update({
            "user_id": str(user.id),
            "username": username,
            "type": request.type
        })
        
        # Get the redirect URL from metadata if available, otherwise use default
        success_url = metadata.get("redirect_url", f"{APP_URL}/wallet?payment_success=true")
        if "?" in success_url:
            success_url = success_url + "&payment_success=true"
        else:
            success_url = success_url + "?payment_success=true"
            
        cancel_url = f"{APP_URL}/wallet?payment_canceled=true"
        print(f"Success URL: {success_url}")
        print(f"Cancel URL: {cancel_url}")
        
        # Different settings based on if this is for adding a payment method or depositing
        print(f"Creating session of type: {request.type}")
        try:
            if request.type == 'setup':
                # This is for setting up a payment method only
                print("Creating setup session")
                session = stripe.checkout.Session.create(
                    customer=customer_id,
                    payment_method_types=["card"],
                    mode="setup",
                    success_url=success_url,
                    cancel_url=cancel_url,
                    metadata=metadata
                )
                
                print(f"Setup session created: {session.id}, URL: {session.url}")
                return {"url": session.url, "session_id": session.id}
            else:
                # This is for a regular deposit or payment
                print(f"Creating payment session for {request.amount} {request.currency}")
                session = stripe.checkout.Session.create(
                    customer=customer_id,
                    payment_method_types=["card"],
                    mode="payment",
                    success_url=success_url,
                    cancel_url=cancel_url,
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
                
                print(f"Payment session created: {session.id}, URL: {session.url}")
                
                # Update wallet immediately for development
                # In production this would be handled by webhook
                try:
                    amount_dollars = request.amount / 100.0  # Convert cents to dollars
                    
                    # Get user's wallet directly instead of using update_wallet_balance
                    # This prevents the creation of a self-deposit transaction
                    user_wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
                    
                    if not user_wallet:
                        # Create wallet if it doesn't exist
                        user_wallet = Wallet(
                        user_id=user.id,
                            fiat_balance=amount_dollars,
                            stablecoin_balance=0,
                            base_currency=request.currency.upper(),
                            display_currency=request.currency.upper()
                        )
                        db.add(user_wallet)
                    else:
                        # Update existing wallet
                        user_wallet.fiat_balance += amount_dollars
                    
                    # Create direct deposit transaction record
                    transaction = Transaction(
                        sender_id=user.id,
                        recipient_id=user.id,
                        stablecoin_amount=amount_dollars,
                        source_amount=amount_dollars,
                        source_currency=request.currency.upper(),
                        target_amount=amount_dollars,
                        target_currency=request.currency.upper(),
                        source_to_stablecoin_rate=1.0,
                        stablecoin_to_target_rate=1.0,
                        status="completed",
                        payment_source="card",
                        transaction_type="DIRECT_DEPOSIT",
                        description=f"Deposit via Stripe"
                    )
                    db.add(transaction)
                    db.commit()
                    
                    print(f"Updated wallet for user {user.id}, added {amount_dollars} {request.currency.upper()}")
                except Exception as wallet_error:
                    print(f"Failed to update wallet, but continuing: {str(wallet_error)}")
                    # Don't fail the request just because wallet update failed
                
                print(f"Returning session URL: {session.url}")
                return {"url": session.url, "session_id": session.id}
        except stripe.error.StripeError as stripe_error:
            print(f"Stripe API error: {str(stripe_error)}")
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(stripe_error)}")
    
    except stripe.error.StripeError as e:
        print(f"Stripe error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        print(f"Unexpected error in create_checkout_session: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/withdraw")
async def process_withdrawal(
    request: WithdrawalRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Process a withdrawal using Stripe's Payout API"""
    print(f"Withdrawal request received: {request}")
    
    try:
        # Verify user permissions
        current_user = db.query(User).filter(User.username == username).first()
        if not current_user:
            return {"success": False, "error": "User not found"}
            
        if current_user.id != request.user_id and not current_user.is_admin:
            return {"success": False, "error": "Not authorized to perform this withdrawal"}
        
        # Get user wallet
        wallet = db.query(Wallet).filter(Wallet.user_id == request.user_id).first()
        if not wallet:
            return {"success": False, "error": "Wallet not found"}
        
        amount_dollars = request.amount / 100.0  # Convert cents to dollars
        
        # Check sufficient funds
        if wallet.fiat_balance < amount_dollars:
        return {
                "success": False, 
                "error": f"Insufficient funds. Available: ${wallet.fiat_balance}, Requested: ${amount_dollars}"
            }
            
        # Get or create customer
        customer_id = get_or_create_customer(db, request.user_id)
            
        # Create an external account (bank account) for this customer if needed
        try:
            # First check if this customer already has any external accounts
            external_accounts = stripe.Customer.list_external_accounts(
                customer_id,
                object="bank_account",
                limit=1
            )
            
            if external_accounts and len(external_accounts.data) > 0:
                # Use existing external account
                destination = external_accounts.data[0].id
                print(f"Using existing bank account: {destination}")
            else:
                # Create a new test bank account token
                bank_account_token = stripe.Token.create(
                    bank_account={
                        "country": "US",
                        "currency": "usd",
                        "account_holder_name": f"{current_user.first_name} {current_user.last_name}" if current_user.first_name else current_user.username,
                        "account_holder_type": "individual",
                        "routing_number": "110000000",  # Test routing number
                        "account_number": "000123456789",  # Test account number
                    },
                )
                
                # Attach the bank account to the customer
                bank_account_object = stripe.Customer.create_source(
                    customer_id,
                    source=bank_account_token.id,
                )
                
                destination = bank_account_object.id
                print(f"Created test bank account: {destination}")
                
                # Create a record in our database
                bank_account = BankAccount(
                    user_id=request.user_id,
                    stripe_bank_id=destination,
                    bank_name="Test Bank",
                    account_type="checking",
                    last4="6789",
                    country="US",
                    currency="usd",
                    status="active",
                    metadata=json.dumps({"test_account": True})
                )
                db.add(bank_account)
                db.flush()
                request.bank_account_id = str(bank_account.id)
            
            # Create the payout
            payout = stripe.Payout.create(
                amount=request.amount,  # Amount in cents
                currency=request.currency.lower(),
                method="standard",
                destination=destination,
            metadata={
                    "user_id": str(request.user_id),
                    "bank_account_id": request.bank_account_id,
                    "transaction_type": "withdrawal"
                }
            )
            
            # Get bank account details for the transaction record
            bank_account = db.query(BankAccount).filter(
                BankAccount.id == request.bank_account_id
            ).first()
            
            bank_name = "Bank Account"
            bank_last4 = "****"
            
            if bank_account:
                bank_name = bank_account.bank_name
                bank_last4 = bank_account.last4
            
            # Deduct from wallet balance
            wallet.fiat_balance -= amount_dollars
            
            # Create transaction record
            transaction = Transaction(
                sender_id=request.user_id,
                recipient_id=request.user_id,  # Self-transaction for withdrawal
                stablecoin_amount=amount_dollars,
                source_amount=amount_dollars,
                source_currency=request.currency.upper(),
                target_amount=amount_dollars,
                target_currency=request.currency.upper(),
                source_to_stablecoin_rate=1.0,
                stablecoin_to_target_rate=1.0,
                status=payout.status,
                payment_source="bank",
                transaction_type="WITHDRAWAL",
                description=f"Withdrawal to {bank_name} •••• {bank_last4}"
            )
            
            db.add(transaction)
            db.commit()
            
            print(f"Withdrawal processed: User {request.user_id}, Amount ${amount_dollars}")
            
            # Return success response
            return {
                "success": True,
                "transaction_id": transaction.id,
                "payout_id": payout.id,
                "amount": amount_dollars,
                "currency": request.currency.upper(),
                "bank_account": f"{bank_name} •••• {bank_last4}",
                "status": payout.status,
                "message": "Withdrawal processed successfully. Funds will arrive in your bank account in 1-3 business days."
            }
            
        except stripe.error.StripeError as se:
            # Handle specific Stripe errors
            error_msg = f"Stripe API error: {str(se)}"
            print(error_msg)
            return {"success": False, "error": error_msg}
        
    except Exception as e:
        db.rollback()
        error_msg = f"Withdrawal failed: {str(e)}"
        print(error_msg)
        return {"success": False, "error": error_msg}
