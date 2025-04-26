"""Base interfaces for payment providers."""

from typing import Dict, Any, Optional, Protocol
from datetime import datetime

class BankAccount(Protocol):
    """Protocol for bank accounts."""
    routing_number: str
    account_number: str
    country_code: str

class TransactionResult(Protocol):
    """Protocol for transaction results."""
    id: str
    status: str
    settled_at: datetime

class PaymentProvider(Protocol):
    """Protocol for payment providers."""
    
    async def pull(self, amount: float, currency: str, account: BankAccount, **kwargs) -> TransactionResult:
        """Pull funds from an account."""
        ...
    
    async def push(self, amount: float, currency: str, account: BankAccount, **kwargs) -> TransactionResult:
        """Push funds to an account."""
        ...

class BridgeProvider(Protocol):
    """Protocol for cross-chain bridge providers."""
    
    async def onramp(
        self,
        amount: float,
        currency: str,
        src_chain: str,
        dst_chain: str,
        recipient: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Bridge tokens from source chain to destination chain.
        
        Args:
            amount: The amount to bridge
            currency: The currency to use
            src_chain: Source chain ID
            dst_chain: Destination chain ID
            recipient: Recipient address
            metadata: Optional additional metadata
            
        Returns:
            A dictionary with the transaction ID and status
        """
        ...
    
    async def offramp(
        self,
        amount: float,
        currency: str,
        chain: str,
        bank_account_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Offramp tokens to fiat.
        
        Args:
            amount: The amount to offramp
            currency: The currency to use
            chain: The chain ID where the tokens are
            bank_account_id: The bank account to send fiat to
            metadata: Optional additional metadata
            
        Returns:
            A dictionary with the transaction ID and status
        """
        ... 