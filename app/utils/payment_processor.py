from typing import Dict, List, Optional, Tuple, Any, Union
import json
from sqlalchemy.orm import Session
from app.models import User, Wallet, Transaction, BlockchainWallet, BlockchainTransaction
from app.utils.binance_api import get_binance_client
from app.blockchain.wallet import WalletManager
from fastapi import HTTPException
import uuid
from decimal import Decimal

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
    
    def process_transfer(
        self,
        sender_id: int,
        recipient_id: int,
        amount: float,
        source_currency: str,
        target_currency: Optional[str] = None,
        description: str = "",
        use_stablecoin: bool = True  # Whether to use stablecoins as intermediary
    ) -> Dict[str, Any]:
        """
        Process a transfer between users, handling currency conversion
        
        Args:
            sender_id: Sender user ID
            recipient_id: Recipient user ID
            amount: Transfer amount
            source_currency: Currency to send
            target_currency: Currency to receive (defaults to recipient's wallet currency)
            description: Transaction description
            use_stablecoin: Whether to use stablecoins as intermediary for cross-currency
            
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
        
        # Use recipient's currency as target if not specified
        if not target_currency:
            target_currency = recipient_wallet.base_currency
            
        # Validate sender has the source currency as their base
        if source_currency != sender_wallet.base_currency:
            raise HTTPException(
                status_code=400,
                detail=f"Sender wallet is in {sender_wallet.base_currency}, not {source_currency}"
            )
            
        # Validate recipient has the target currency as their base
        if target_currency != recipient_wallet.base_currency:
            raise HTTPException(
                status_code=400,
                detail=f"Recipient wallet is in {recipient_wallet.base_currency}, not {target_currency}"
            )
            
        # Check sufficient balance
        if sender_wallet.fiat_balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
            
        # Start transfer process
        stablecoin_amount = amount
        target_amount = amount
        source_to_stablecoin_rate = 1.0
        stablecoin_to_target_rate = 1.0
            
        # Handle currency conversion using stablecoin as intermediary if needed
        if source_currency != target_currency and use_stablecoin:
            # Convert source to stablecoin (USDT)
            source_to_stablecoin_rate = self.binance_client.get_stablecoin_conversion_rate(
                source_currency, 
                "USDT"
            )
            
            if not source_to_stablecoin_rate:
                # Fallback to our conversion utility
                from app.utils.conversion import fetch_conversion_rate
                source_to_stablecoin_rate = fetch_conversion_rate(source_currency, "USDT")
                
            # Calculate intermediate USDT (stablecoin) amount
            stablecoin_amount = amount * source_to_stablecoin_rate
            
            # Convert stablecoin to target currency
            stablecoin_to_target_rate = self.binance_client.get_stablecoin_conversion_rate(
                "USDT",
                target_currency
            )
            
            if not stablecoin_to_target_rate:
                # Fallback to our conversion utility
                from app.utils.conversion import fetch_conversion_rate
                stablecoin_to_target_rate = fetch_conversion_rate("USDT", target_currency)
                
            # Calculate final target amount
            target_amount = stablecoin_amount * stablecoin_to_target_rate
        elif source_currency != target_currency:
            # Direct conversion without stablecoin intermediary
            direct_rate = self.binance_client.get_stablecoin_conversion_rate(
                source_currency,
                target_currency
            )
            
            if not direct_rate:
                # Fallback to our conversion utility
                from app.utils.conversion import fetch_conversion_rate
                direct_rate = fetch_conversion_rate(source_currency, target_currency)
                
            target_amount = amount * direct_rate
            # For simplified accounting, treat as if stablecoin was used
            stablecoin_amount = amount  
            source_to_stablecoin_rate = 1.0
            stablecoin_to_target_rate = direct_rate
        
        # Process the transfer
        sender_wallet.fiat_balance -= amount
        recipient_wallet.fiat_balance += target_amount
        
        # Record the transaction
        transaction = Transaction(
            sender_id=sender_id,
            recipient_id=recipient_id,
            stablecoin_amount=stablecoin_amount,
            source_amount=amount,
            source_currency=source_currency,
            target_amount=target_amount,
            target_currency=target_currency,
            source_to_stablecoin_rate=source_to_stablecoin_rate,
            stablecoin_to_target_rate=stablecoin_to_target_rate,
            status="completed",
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        self.db.refresh(sender_wallet)
        self.db.refresh(recipient_wallet)
        
        return {
            "success": True,
            "transaction_id": transaction.id,
            "source_amount": amount,
            "source_currency": source_currency,
            "target_amount": target_amount,
            "target_currency": target_currency,
            "sender_new_balance": sender_wallet.fiat_balance,
            "recipient_new_balance": recipient_wallet.fiat_balance,
            "description": description
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