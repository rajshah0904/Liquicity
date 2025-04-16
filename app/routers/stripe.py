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
        process_direct_deposit(
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
            BankAccount.user_id == request.user_id,
            BankAccount.status == "active"
        ).first()
        
        if not bank_account:
            raise HTTPException(status_code=404, detail="Bank account not found or inactive")
        
        # Check wallet balance
        wallet = db.query(Wallet).filter(Wallet.user_id == request.user_id).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        amount_dollars = request.amount / 100.0  # Convert cents to dollars
        if wallet.fiat_balance < amount_dollars:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        
        try:
            # Create ACH transfer using the existing bank account
            transfer = stripe.Transfer.create(
                amount=request.amount,  # Amount in cents
                currency=request.currency.lower(),
                destination=bank_account.stripe_bank_id,
                description=f"Withdrawal to {bank_account.bank_name} •••• {bank_account.last4}",
                metadata={
                    "user_id": str(request.user_id),
                    "bank_account_id": str(request.bank_account_id),
                    "transaction_type": "withdrawal"
                }
            )
            
            # Deduct from wallet immediately
            wallet.fiat_balance -= amount_dollars
            
            # Create withdrawal transaction record
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
                status="processing",  # Will be updated by webhook
                payment_source="bank",
                transaction_type="WITHDRAWAL",
                description=f"Withdrawal to {bank_account.bank_name} •••• {bank_account.last4}"
            )
            
            db.add(transaction)
            db.commit()
            
            print(f"Processing withdrawal: Amount=${amount_dollars} to bank account {bank_account.last4}")
            
            return {
                "success": True,
                "transfer_id": transfer.id,
                "amount": amount_dollars,
                "currency": request.currency.upper(),
                "bank_account": f"{bank_account.bank_name} •••• {bank_account.last4}",
                "status": transfer.status,
                "estimated_arrival": "1-3 business days"
            }
            
        except stripe.error.StripeError as e:
            print(f"Stripe error during withdrawal: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Withdrawal failed: {str(e)}")
            
    except Exception as e:
        print(f"Error processing withdrawal: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Withdrawal failed: {str(e)}")

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
                    process_direct_deposit,
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
            recipient_id = metadata.get("recipient_id")
            transaction_type = metadata.get("transaction_type", "payment")
            
            if user_id:
                # Update wallet balance
                amount_cents = payment_intent.get("amount", 0)
                amount_dollars = amount_cents / 100.0
                currency = payment_intent.get("currency", "usd")
                
                # Update in background
                if recipient_id and recipient_id != user_id:
                    # This is a payment to another user, not a deposit
                    background_tasks.add_task(
                        process_payment_transfer,
                        db=db,
                        sender_id=int(user_id),
                        recipient_id=int(recipient_id),
                        amount=amount_dollars,
                        currency=currency.upper(),
                        transaction_type=transaction_type
                    )
                else:
                    # This is a direct deposit to the user's own wallet
                    background_tasks.add_task(
                        process_direct_deposit,
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

@router.post("/direct-payment")
async def process_direct_payment(
    request: DirectPaymentRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Process a direct payment using a stored Stripe payment method"""
    try:
        # Verify user
        current_user = db.query(User).filter(User.username == username).first()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Extract transaction data
        transaction_data = request.transaction
        recipient_id = transaction_data.get("recipient_id")
        amount = float(transaction_data.get("amount", 0))
        source_currency = transaction_data.get("currency", "USD")
        
        # Verify recipient exists
        recipient = db.query(User).filter(User.id == recipient_id).first()
        if not recipient:
            raise HTTPException(status_code=404, detail="Recipient not found")
        
        # Convert amount to cents for Stripe
        amount_cents = int(amount * 100)
        
        # If wallet_partial, use part of wallet balance
        wallet_amount = 0
        if request.payment_source == "wallet_partial":
            wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
            if wallet:
                wallet_amount = min(wallet.fiat_balance, amount)
                # Calculate remaining amount to charge via Stripe
                remaining_amount = amount - wallet_amount
                # Update amount_cents for Stripe charge
                amount_cents = int(remaining_amount * 100)
        
        # Create a payment intent with Stripe
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=source_currency.lower(),
            customer=current_user.stripe_customer_id,
            payment_method=request.payment_method_id,
            confirm=True,  # Confirm immediately
            return_url=f"{APP_URL}/send?payment_success=true",
            metadata={
                "user_id": str(current_user.id),
                "recipient_id": str(recipient_id),
                "transaction_type": "payment",
                "payment_source": request.payment_source,
                "wallet_amount": str(wallet_amount)
            }
        )
        
        # Handle successful payment
        if payment_intent.status in ["succeeded", "processing", "requires_capture"]:
            # Process the payment transfer directly, similar to bank account payments
            process_payment_transfer(
                db=db,
                sender_id=current_user.id,
                recipient_id=recipient_id,
                amount=amount,
                currency=source_currency.upper(),
                transaction_type="STRIPE_PAYMENT"
            )
            
            # If using wallet_partial, deduct from sender's wallet
            if request.payment_source == "wallet_partial" and wallet_amount > 0:
                wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
                if wallet:
                    wallet.fiat_balance -= wallet_amount
                    db.commit()
            
            return {
                "success": True,
                "payment_intent_id": payment_intent.id,
                "status": payment_intent.status
            }
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Payment failed with status: {payment_intent.status}"
            )
    
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payment-methods/{user_id}")
async def get_payment_methods(
    user_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Get all payment methods for a user"""
    try:
        # Check if authorized
        current_user = db.query(User).filter(User.username == username).first()
        if not current_user or (current_user.id != user_id and not current_user.is_admin):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user.stripe_customer_id:
            return []
        
        # Get payment methods from Stripe
        payment_methods = stripe.PaymentMethod.list(
            customer=user.stripe_customer_id,
            type="card"
        )
        
        # Add bank accounts
        bank_accounts = stripe.PaymentMethod.list(
            customer=user.stripe_customer_id,
            type="us_bank_account"
        )
        
        # Format response
        result = []
        
        # Add cards
        for method in payment_methods.data:
            result.append({
                "id": method.id,
                "type": "card",
                "last4": method.card.last4,
                "brand": method.card.brand,
                "exp_month": method.card.exp_month,
                "exp_year": method.card.exp_year
            })
        
        # Add bank accounts
        for method in bank_accounts.data:
            result.append({
                "id": method.id,
                "type": "bank",
                "last4": method.us_bank_account.last4,
                "bank_name": method.us_bank_account.bank_name
            })
        
        return result
    
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def process_direct_deposit(db: Session, user_id: int, amount: float, currency: str, transaction_type: str = "deposit"):
    """
    Process a direct deposit to a user's wallet without creating a self-transaction
    """
    try:
        # Find or create user wallet
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
        
        if not wallet:
            wallet = Wallet(
                user_id=user_id,
                fiat_balance=amount,
                stablecoin_balance=0,
                base_currency=currency,
                display_currency=currency
            )
            db.add(wallet)
        else:
            wallet.fiat_balance += amount
        
        # Create a single transaction record marked as direct deposit
        transaction = Transaction(
            sender_id=user_id,
            recipient_id=user_id,
            stablecoin_amount=amount,
            source_amount=amount,
            source_currency=currency,
            target_amount=amount,
            target_currency=currency,
            source_to_stablecoin_rate=1.0,
            stablecoin_to_target_rate=1.0,
            status="completed",
            payment_source="stripe",
            transaction_type="DIRECT_DEPOSIT",
            description=f"{transaction_type.capitalize()} via Stripe"
        )
        
        db.add(transaction)
        db.commit()
        print(f"Direct deposit processed: User {user_id}, amount {amount} {currency}")
        
    except Exception as e:
        print(f"Error processing direct deposit: {str(e)}")
        db.rollback()

def process_payment_transfer(db: Session, sender_id: int, recipient_id: int, amount: float, currency: str, transaction_type: str = "payment"):
    """
    Process a payment transfer from one user to another
    """
    try:
        # Get recipient wallet
        recipient_wallet = db.query(Wallet).filter(Wallet.user_id == recipient_id).first()
        
        if not recipient_wallet:
            print(f"Creating new wallet for recipient {recipient_id}")
            recipient_wallet = Wallet(
                user_id=recipient_id,
                fiat_balance=amount,
                stablecoin_balance=0,
                base_currency=currency,
                display_currency=currency
            )
            db.add(recipient_wallet)
        else:
            print(f"Updating existing wallet for recipient {recipient_id}")
            print(f"Previous balance: {recipient_wallet.fiat_balance} {currency}")
            recipient_wallet.fiat_balance += amount
            print(f"New balance: {recipient_wallet.fiat_balance} {currency}")
        
        # Create a transaction record
        transaction = Transaction(
            sender_id=sender_id,
            recipient_id=recipient_id,
            stablecoin_amount=amount,
            source_amount=amount,
            source_currency=currency,
            target_amount=amount,
            target_currency=currency,
            source_to_stablecoin_rate=1.0,
            stablecoin_to_target_rate=1.0,
            status="completed",
            payment_source="stripe",
            transaction_type="STRIPE_PAYMENT",
            description=f"Payment via Stripe"
        )
        
        db.add(transaction)
        db.commit()
        print(f"Payment transfer processed: From {sender_id} to {recipient_id}, amount {amount} {currency}")
        print(f"Transaction ID: {transaction.id}")
        
        # Verify the recipient's wallet was updated
        db.refresh(recipient_wallet)
        print(f"Final recipient wallet balance: {recipient_wallet.fiat_balance} {currency}")
        
    except Exception as e:
        print(f"Error processing payment transfer: {str(e)}")
        db.rollback()
        raise

# This function is kept for backward compatibility but uses the newer functions internally
def update_wallet_balance(db: Session, user_id: int, amount: float, currency: str, transaction_type: str):
    """
    DEPRECATED: Update user wallet balance
    This uses process_direct_deposit internally to avoid the double-crediting issue
    """
    print(f"DEPRECATED: update_wallet_balance called. Use process_direct_deposit instead.")
    
    if transaction_type == "withdrawal":
        # For withdrawals, we need to negate the amount
        process_direct_deposit(
            db=db,
            user_id=user_id,
            amount=-amount,  # Negate for withdrawal
            currency=currency,
            transaction_type="withdrawal"
        )
    else:
        # For deposits or other types
        process_direct_deposit(
            db=db,
            user_id=user_id,
            amount=amount,
            currency=currency,
            transaction_type=transaction_type
        ) 