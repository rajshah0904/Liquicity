"""
Stablecoin provider interfaces for TerraFlow.

This module defines the base interfaces for stablecoin operations, including
minting (converting fiat to stablecoin) and redemption (converting stablecoin to fiat).
"""

from typing import Protocol, Dict, Any, Optional
from datetime import datetime

class StablecoinResult(Protocol):
    """
    Protocol defining the result of a stablecoin operation.
    
    This interface provides a standardized way to represent the result of 
    stablecoin operations like minting and redemption across different providers.
    """
    
    tx_id: str  # Blockchain transaction ID or provider-specific identifier
    status: str  # Status of the transaction (e.g., "pending", "completed", "failed")
    settled_at: datetime  # When the transaction was or will be settled

class StablecoinProvider(Protocol):
    """
    Protocol defining the interface for stablecoin providers.
    
    This interface abstracts the common operations that all stablecoin providers
    should implement, allowing for interchangeable use of different stablecoin
    implementations (USDC, USDT, etc.).
    """
    
    async def mint(
        self, 
        amount: float, 
        currency: str, 
        chain: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> StablecoinResult:
        """
        Mint stablecoins by converting fiat currency.
        
        This operation converts fiat currency to stablecoins on a specified blockchain.
        
        Args:
            amount: The amount of stablecoins to mint
            currency: The fiat currency to convert from (e.g., "USD", "EUR")
            chain: The blockchain to mint on (e.g., "ethereum", "polygon", "solana")
            metadata: Optional additional data to attach to the transaction
            
        Returns:
            A StablecoinResult containing the transaction ID and status
            
        Raises:
            ValueError: If the mint operation fails
        """
        ...
    
    async def redeem(
        self, 
        amount: float, 
        currency: str, 
        bank_account_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> StablecoinResult:
        """
        Redeem stablecoins for fiat currency.
        
        This operation converts stablecoins back to fiat currency and transfers
        the funds to a specified bank account.
        
        Args:
            amount: The amount of stablecoins to redeem
            currency: The fiat currency to receive (e.g., "USD", "EUR")
            bank_account_id: The ID of the bank account to send the fiat currency to
            metadata: Optional additional data to attach to the transaction
            
        Returns:
            A StablecoinResult containing the transaction ID and status
            
        Raises:
            ValueError: If the redemption operation fails
        """
        ...
        
    async def get_balance(
        self,
        wallet_address: str,
        chain: Optional[str] = None
    ) -> float:
        """
        Get the stablecoin balance for a wallet address.
        
        Args:
            wallet_address: The blockchain wallet address to check
            chain: Optional blockchain to check (if None, checks the default chain)
            
        Returns:
            The stablecoin balance as a float
            
        Raises:
            ValueError: If the balance check fails
        """
        ...
        
    async def get_transaction_status(
        self,
        tx_id: str
    ) -> str:
        """
        Get the current status of a stablecoin transaction.
        
        Args:
            tx_id: The transaction ID to check
            
        Returns:
            The status of the transaction (e.g., "pending", "completed", "failed")
            
        Raises:
            ValueError: If the transaction status check fails
        """
        ... 