from typing import Dict, List, Optional, Tuple, Any, Union
import json
from sqlalchemy.orm import Session
from app.models import User, Wallet, Transaction, BlockchainWallet, BlockchainTransaction
from app.utils.binance_api import get_binance_client
from app.blockchain.wallet import WalletManager
from fastapi import HTTPException
import uuid
from decimal import Decimal
from datetime import datetime, timedelta

class PaymentProcessor:
    """
    Central payment processing service for TerraFlow
    Handles deposits, withdrawals, and cross-currency transfers
    """
    
    def __init__(self, db: Session):
        """Initialize with database session"""
        self.db = db
        self.binance_client = get_binance_client()
        
    def process_deposit(
        self, 
        user_id: int, 
        amount: float, 
        currency: str,
        payment_method: str = "bank_transfer",
        payment_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a deposit to a user's wallet
        
        Args:
            user_id: Target user ID
            amount: Deposit amount
            currency: Currency code (e.g., 'USD', 'EUR')
            payment_method: Method used for deposit
            payment_details: Additional payment information
            
        Returns:
            Dictionary with deposit result
        """
        # Validate inputs
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Deposit amount must be positive")

        # Get user wallet
        wallet = self.db.query(Wallet).filter(Wallet.user_id == user_id).first()
        
        # Auto-create wallet if it doesn't exist
        if not wallet:
            wallet = Wallet(
                user_id=user_id,
                fiat_balance=0,
                stablecoin_balance=0,
                base_currency=currency,
                display_currency=currency
            )
            self.db.add(wallet)
            self.db.commit()
            self.db.refresh(wallet)

        # Process based on deposit currency
        original_amount = amount
        
        # If deposit currency matches wallet base currency
        if currency == wallet.base_currency:
            wallet.fiat_balance += amount
        else:
            # Convert to wallet's base currency
            conversion_rate = self.binance_client.get_stablecoin_conversion_rate(
                currency, 
                wallet.base_currency
            )
            
            if not conversion_rate:
                # Fallback to our conversion utility
                from app.utils.conversion import fetch_conversion_rate
                conversion_rate = fetch_conversion_rate(currency, wallet.base_currency)
            
            converted_amount = amount * conversion_rate
            wallet.fiat_balance += converted_amount

        # Record the deposit as a transaction (self-transfer)
        # In a real system, you'd integrate with payment processor webhooks
        transaction = Transaction(
            sender_id=user_id,  # Self-deposit
            recipient_id=user_id,
            stablecoin_amount=amount,  # Using 1:1 for simplicity
            source_amount=original_amount,
            source_currency=currency,
            target_amount=amount,
            target_currency=wallet.base_currency,
            source_to_stablecoin_rate=1.0,  # Direct deposit, no conversion
            stablecoin_to_target_rate=1.0,
            status="completed"
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(wallet)
        self.db.refresh(transaction)
        
        return {
            "success": True,
            "deposit_id": transaction.id,
            "amount": original_amount,
            "currency": currency,
            "new_balance": wallet.fiat_balance,
            "wallet_currency": wallet.base_currency
        }

    def process_withdrawal(
        self, 
        user_id: int, 
        amount: float, 
        currency: str,
        withdrawal_method: str = "bank_transfer",
        withdrawal_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a withdrawal from a user's wallet
        
        Args:
            user_id: User ID
            amount: Withdrawal amount
            currency: Currency code
            withdrawal_method: Method for withdrawal
            withdrawal_details: Bank info or other withdrawal details
            
        Returns:
            Dictionary with withdrawal result
        """
        # Validate inputs
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Withdrawal amount must be positive")

        # Get user wallet
        wallet = self.db.query(Wallet).filter(Wallet.user_id == user_id).first()
        
        if not wallet:
            raise HTTPException(status_code=404, detail="User wallet not found")

        # Convert to wallet currency if needed
        withdrawal_amount = amount
        
        if currency != wallet.base_currency:
            # Need to convert
            conversion_rate = self.binance_client.get_stablecoin_conversion_rate(
                wallet.base_currency,
                currency
            )
            
            if not conversion_rate:
                # Fallback to our conversion utility
                from app.utils.conversion import fetch_conversion_rate
                conversion_rate = fetch_conversion_rate(wallet.base_currency, currency)
            
            withdrawal_amount = amount / conversion_rate

        # Check sufficient funds
        if wallet.fiat_balance < withdrawal_amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        # Process withdrawal
        wallet.fiat_balance -= withdrawal_amount

        # Record transaction
        transaction = Transaction(
            sender_id=user_id,
            recipient_id=user_id,  # Self-withdrawal
            stablecoin_amount=amount,
            source_amount=withdrawal_amount,
            source_currency=wallet.base_currency,
            target_amount=amount,
            target_currency=currency,
            source_to_stablecoin_rate=1.0,
            stablecoin_to_target_rate=1.0,
            status="completed"
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(wallet)
        self.db.refresh(transaction)
        
        return {
            "success": True,
            "withdrawal_id": transaction.id,
            "amount": amount,
            "currency": currency,
            "new_balance": wallet.fiat_balance,
            "wallet_currency": wallet.base_currency
        }
    
    def fix_stripe_balance(self, user_id: int, amount: float, source_currency: str, transaction_timestamp = None):
        """
        Automatically fix balance issues caused by Stripe payments.
        This method checks if a user has a self-deposit transaction that matches
        the amount of a Stripe payment made to another user, and if found, voids 
        the self-deposit and adjusts the wallet balance.
        
        Args:
            user_id: The user ID to check/fix
            amount: The amount of the transaction
            source_currency: The currency code
            transaction_timestamp: Optional timestamp of the transaction
            
        Returns:
            dict with results of the fix
        """
        # If no timestamp provided, use current time
        if transaction_timestamp is None:
            transaction_timestamp = datetime.utcnow()
            
        # Find a matching self-deposit that happened around the same time
        # This is a transaction where the user sent money to themselves
        # with the same amount around this time
        try:
            matching_deposit = self.db.query(Transaction).filter(
                Transaction.sender_id == user_id,
                Transaction.recipient_id == user_id,
                Transaction.source_amount == amount,
                Transaction.source_currency == source_currency,
                Transaction.status == "completed"
            ).filter(
                Transaction.timestamp >= transaction_timestamp - timedelta(minutes=2),
                Transaction.timestamp <= transaction_timestamp + timedelta(minutes=2)
            ).first()
            
            if not matching_deposit:
                return {"success": True, "fixed": False, "message": "No matching self-deposit found"}
                
            # Found a matching self-deposit, adjust the user's wallet
            wallet = self.db.query(Wallet).filter(Wallet.user_id == user_id).first()
            
            if not wallet:
                return {"success": False, "message": "Wallet not found"}
                
            # Subtract the deposit amount from the wallet
            original_balance = wallet.fiat_balance
            wallet.fiat_balance = max(0, wallet.fiat_balance - amount)
            
            # Mark the self-deposit as voided
            matching_deposit.status = "voided"
            
            # Commit changes
            self.db.commit()
            
            print(f"Fixed balance issue: Adjusted user {user_id}'s balance from {original_balance} to {wallet.fiat_balance}")
            
            return {
                "success": True,
                "fixed": True,
                "deposit_id": matching_deposit.id,
                "amount": amount,
                "old_balance": original_balance,
                "new_balance": wallet.fiat_balance
            }
            
        except Exception as e:
            # Log the error but don't fail the transaction
            print(f"Error fixing stripe balance: {str(e)}")
            return {"success": False, "message": f"Error fixing balance: {str(e)}"}
    
    def process_transfer(
        self,
        sender_id: int,
        recipient_id: int,
        amount: float,
        source_currency: str,
        target_currency: Optional[str] = None,
        description: Optional[str] = None,
        use_stablecoin: bool = True,
        stripe_payment: bool = False,
        skip_sender_deduction: bool = False,
        **kwargs  # Catch any extra parameters we don't need
    ) -> Dict[str, Any]:
        """Process a transfer between users, handling currency conversion"""
        # Add debugging
        print(f"Processing transfer: sender={sender_id}, recipient={recipient_id}, amount={amount}, stripe={stripe_payment}")
        
        # IMPORTANT: Check for and prevent self-deposits from Stripe
        # This is the root cause of the double-crediting issue
        payment_source = kwargs.get('payment_source', None)
        if (stripe_payment or payment_source in ['card', 'bank']) and sender_id == recipient_id:
            print(f"WARNING: Attempted self-deposit with Stripe payment: user_id={sender_id}, amount={amount}, currency={source_currency}")
            # Instead of creating a self-deposit transaction, create a record of a direct deposit
            transaction = Transaction(
                sender_id=sender_id,
                recipient_id=recipient_id,
                stablecoin_amount=amount,
                source_amount=amount,
                source_currency=source_currency,
                target_amount=amount,
                target_currency=target_currency or source_currency,
                source_to_stablecoin_rate=1.0,
                stablecoin_to_target_rate=1.0,
                status="completed",
                payment_source=payment_source,
                transaction_type="DIRECT_DEPOSIT"  # Mark as direct deposit instead of transfer
            )
            
            self.db.add(transaction)
            
            # Get or create the user's wallet
            wallet = self.db.query(Wallet).filter(Wallet.user_id == sender_id).first()
            if not wallet:
                wallet = Wallet(
                    user_id=sender_id,
                    fiat_balance=amount,
                    stablecoin_balance=0,
                    base_currency=source_currency,
                    display_currency=source_currency
                )
                self.db.add(wallet)
            else:
                # Only add to wallet balance once
                wallet.fiat_balance += amount
            
            self.db.commit()
            
            print(f"Direct deposit processed: ID={transaction.id}, new balance={wallet.fiat_balance}")
            
            return {
                "transaction_id": transaction.id,
                "source_amount": amount,
                "source_currency": source_currency,
                "target_amount": amount,
                "target_currency": target_currency or source_currency,
                "sender_new_balance": wallet.fiat_balance,
                "recipient_new_balance": wallet.fiat_balance
            }
        
        if target_currency is None:
            target_currency = source_currency

        # Get sender wallet
        sender_wallet = self.db.query(Wallet).filter(Wallet.user_id == sender_id).first()
        if not sender_wallet:
            raise ValueError(f"No wallet found for sender (user_id={sender_id})")
        
        # Get or create recipient wallet
        recipient_wallet = self.db.query(Wallet).filter(Wallet.user_id == recipient_id).first()
        if not recipient_wallet:
            recipient_wallet = Wallet(
                user_id=recipient_id,
                fiat_balance=0,
                stablecoin_balance=0,
                base_currency=target_currency,
                display_currency=target_currency
            )
            self.db.add(recipient_wallet)
            self.db.flush()

        # Handle sender wallet deduction for non-Stripe payments
        if not stripe_payment and not skip_sender_deduction:
            if sender_wallet.fiat_balance < amount:
                raise ValueError(f"Insufficient balance in sender wallet. Available: {sender_wallet.fiat_balance}, Required: {amount}")
            
            sender_wallet.fiat_balance -= amount

        # Add to recipient's wallet
        recipient_wallet.fiat_balance += amount

        # Create transaction record
        transaction = Transaction(
            sender_id=sender_id,
            recipient_id=recipient_id,
            stablecoin_amount=amount,
            source_amount=amount,
            source_currency=source_currency,
            target_amount=amount,
            target_currency=target_currency,
            source_to_stablecoin_rate=1.0,
            stablecoin_to_target_rate=1.0,
            status="completed",
            payment_source=payment_source,
            transaction_type=kwargs.get('transaction_type', 'TRANSFER')
        )
        
        self.db.add(transaction)
        self.db.commit()
        
        print(f"Transfer complete: ID={transaction.id}, sender balance={sender_wallet.fiat_balance}, recipient balance={recipient_wallet.fiat_balance}")

        return {
            "transaction_id": transaction.id,
            "source_amount": amount,
            "source_currency": source_currency,
            "target_amount": amount,
            "target_currency": target_currency,
            "sender_new_balance": sender_wallet.fiat_balance,
            "recipient_new_balance": recipient_wallet.fiat_balance
        }

    def process_crypto_transfer(
        self,
        sender_id: int,
        recipient_id: int,
        amount: float,
        crypto_currency: str = "USDT",
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Process a direct cryptocurrency transfer between users
        
        Args:
            sender_id: Sender user ID
            recipient_id: Recipient user ID
            amount: Amount of cryptocurrency to transfer
            crypto_currency: Cryptocurrency code (default USDT)
            description: Transaction description
            
        Returns:
            Dictionary with transfer result
        """
        # Get sender and recipient wallets
        sender_wallet = self.db.query(Wallet).filter(Wallet.user_id == sender_id).first()
        recipient_wallet = self.db.query(Wallet).filter(Wallet.user_id == recipient_id).first()

        if not sender_wallet:
            raise HTTPException(status_code=404, detail="Sender wallet not found")
            
        if not recipient_wallet:
            raise HTTPException(status_code=404, detail="Recipient wallet not found")
            
        # Check if cryptocurrency is supported
        if crypto_currency not in ["USDT", "USDC", "BUSD", "DAI"]:
            raise HTTPException(status_code=400, detail=f"Unsupported cryptocurrency: {crypto_currency}")
            
        # Check sufficient stablecoin balance
        if sender_wallet.stablecoin_balance < amount:
            raise HTTPException(status_code=400, detail=f"Insufficient {crypto_currency} balance")

        # Process the transfer
        sender_wallet.stablecoin_balance -= amount
        recipient_wallet.stablecoin_balance += amount

        # Record the transaction
        transaction = Transaction(
            sender_id=sender_id,
            recipient_id=recipient_id,
            stablecoin_amount=amount,
            source_amount=amount,
            source_currency=crypto_currency,
            target_amount=amount,
            target_currency=crypto_currency,
            source_to_stablecoin_rate=1.0,  # Direct stablecoin transfer
            stablecoin_to_target_rate=1.0,
            status="completed"
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        self.db.refresh(sender_wallet)
        self.db.refresh(recipient_wallet)

        return {
            "success": True,
            "transaction_id": transaction.id,
            "amount": amount,
            "crypto_currency": crypto_currency,
            "sender_new_balance": sender_wallet.stablecoin_balance,
            "recipient_new_balance": recipient_wallet.stablecoin_balance,
            "description": description
        }
        
    def process_on_chain_transaction(
        self,
        user_id: int,
        blockchain_wallet_id: int,
        recipient_address: str,
        token_address: str,
        amount: float,
        private_key: str,
        gas_price_gwei: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process an on-chain token transfer (e.g., sending USDT on Ethereum)
        
        Args:
            user_id: User ID
            blockchain_wallet_id: Blockchain wallet ID to use
            recipient_address: Recipient blockchain address
            token_address: Token contract address
            amount: Amount to send
            private_key: Private key for signing (in production, use a secure vault)
            gas_price_gwei: Optional gas price in gwei
            
        Returns:
            Dictionary with transaction result
        """
        # Get user and blockchain wallet
        user = self.db.query(User).filter(User.id == user_id).first()
        blockchain_wallet = self.db.query(BlockchainWallet).filter(
            BlockchainWallet.id == blockchain_wallet_id,
            BlockchainWallet.user_id == user_id
        ).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        if not blockchain_wallet:
            raise HTTPException(status_code=404, detail="Blockchain wallet not found or unauthorized")
            
        # Init wallet manager for the chain
        wallet_manager = WalletManager(chain=blockchain_wallet.chain)

        # Check if wallet has sufficient token balance
        token_balance = wallet_manager.get_token_balance(
            blockchain_wallet.address,
            token_address
        )
        
        if token_balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient token balance")

        # Execute the token transfer
        try:
            tx_hash = wallet_manager.transfer_token(
                from_address=blockchain_wallet.address,
                to_address=recipient_address,
                token_address=token_address,
                amount=amount,
                private_key=private_key,
                gas_price_gwei=gas_price_gwei
            )
            
            # Record the blockchain transaction
            blockchain_tx = wallet_manager.record_transaction_in_db(
                db=self.db,
                txn_hash=tx_hash,
                from_address=blockchain_wallet.address,
                to_address=recipient_address,
                value=str(amount),
                wallet_id=blockchain_wallet.id,
                function_name="transfer",
                function_args={
                    "token_address": token_address,
                    "amount": amount
                }
            )
            
            # Also record in regular transaction table for unified history
            transaction = Transaction(
                sender_id=user_id,
                recipient_id=user_id,  # Self-transaction for on-chain
                stablecoin_amount=amount,
                source_amount=amount,
                source_currency="USDT",  # Assume stablecoin
                target_amount=amount,
                target_currency="USDT",
                blockchain_txn_hash=tx_hash,
                status="pending"  # Will be updated when confirmed
            )
            
            self.db.add(transaction)
            self.db.commit()

            return {
                "success": True,
                "transaction_hash": tx_hash,
                "from_address": blockchain_wallet.address,
                "to_address": recipient_address,
                "amount": amount,
                "token_address": token_address,
                "chain": blockchain_wallet.chain,
                "status": "pending"
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Blockchain transaction failed: {str(e)}")

# Create a function to get the payment processor
def get_payment_processor(db: Session) -> PaymentProcessor:
    """Get a payment processor instance"""
    return PaymentProcessor(db) 