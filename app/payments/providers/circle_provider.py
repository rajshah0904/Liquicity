"""
Circle USDC provider implementation for TerraFlow.

This module provides a Circle API-based implementation of the StablecoinProvider
interface, allowing for minting and redemption of USDC stablecoins.
"""

import os
import uuid
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, cast, Union

from circle import CircleClient
from circle.exceptions import CircleAPIError, CircleNetworkError, CircleTimeoutError

from .stablecoin_base import StablecoinProvider, StablecoinResult

logger = logging.getLogger(__name__)

class CircleStablecoinResult:
    """Implementation of StablecoinResult for Circle"""
    
    def __init__(self, tx_id: str, status: str, settled_at: Optional[datetime] = None):
        self.tx_id = tx_id
        self.status = status
        self.settled_at = settled_at or datetime.now(timezone.utc)

class CircleProvider(StablecoinProvider):
    """
    Circle USDC provider implementation.
    
    This class provides an implementation of the StablecoinProvider interface
    using Circle's API for USDC minting and redemption operations.
    """
    
    def __init__(self):
        """Initialize the Circle provider with API credentials from environment variables."""
        api_key = os.getenv("CIRCLE_API_KEY")
        if not api_key:
            raise ValueError("CIRCLE_API_KEY environment variable is not set")
            
        self.client = CircleClient(api_key=api_key)
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
        # Map of Circle status values to our standardized status values
        self.status_mapping = {
            "pending": "pending",
            "complete": "completed",
            "failed": "failed",
            "processing": "pending",
            "success": "completed",
            "error": "failed"
        }
    
    def _map_status(self, circle_status: str) -> str:
        """Map Circle API status values to our standardized status values."""
        return self.status_mapping.get(circle_status.lower(), "pending")
    
    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse Circle API datetime string to datetime object."""
        if not date_str:
            return None
            
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse datetime: {date_str}: {e}")
            return None
    
    async def _execute_with_retry(self, operation_name: str, operation_func, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute a Circle API operation with retry logic.
        
        Args:
            operation_name: Name of the operation (for logging)
            operation_func: Function to execute
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            The API response data
            
        Raises:
            ValueError: If the operation fails after all retries
        """
        retries = 0
        last_error = None
        
        while retries <= self.max_retries:
            try:
                response = await operation_func(*args, **kwargs)
                return response
                
            except CircleTimeoutError as e:
                # Always retry timeouts
                retries += 1
                last_error = e
                if retries <= self.max_retries:
                    wait_time = self.retry_delay * (2 ** (retries - 1))  # Exponential backoff
                    logger.warning(f"Circle API timeout during {operation_name}. Retrying in {wait_time}s ({retries}/{self.max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Failed after {self.max_retries} retries: {str(e)}")
                    break
                    
            except CircleNetworkError as e:
                # Network errors are retryable
                retries += 1
                last_error = e
                if retries <= self.max_retries:
                    wait_time = self.retry_delay * (2 ** (retries - 1))
                    logger.warning(f"Circle API network error during {operation_name}. Retrying in {wait_time}s ({retries}/{self.max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Failed after {self.max_retries} retries: {str(e)}")
                    break
                    
            except CircleAPIError as e:
                # Some API errors are retryable (rate limits, server errors)
                if e.status_code in [429, 500, 502, 503, 504]:
                    retries += 1
                    last_error = e
                    if retries <= self.max_retries:
                        wait_time = self.retry_delay * (2 ** (retries - 1))
                        logger.warning(f"Circle API error ({e.status_code}) during {operation_name}. Retrying in {wait_time}s ({retries}/{self.max_retries})")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"Failed after {self.max_retries} retries: {str(e)}")
                        break
                else:
                    # Client errors are not retryable
                    logger.error(f"Circle API error ({e.status_code}) during {operation_name}: {e.message}")
                    raise ValueError(f"Circle API error: {e.message}")
            
            except Exception as e:
                # Unexpected errors are not retryable
                logger.error(f"Unexpected error during {operation_name}: {str(e)}")
                raise ValueError(f"Unexpected error during {operation_name}: {str(e)}")
        
        # If we get here, all retries failed
        if last_error:
            logger.error(f"All retries failed for {operation_name}: {str(last_error)}")
            raise ValueError(f"Failed to {operation_name} after multiple retries: {str(last_error)}")
        else:
            raise ValueError(f"Unknown error occurred during {operation_name}")
    
    async def mint(
        self, 
        amount: float, 
        currency: str, 
        chain: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> StablecoinResult:
        """
        Mint USDC stablecoins by converting fiat currency through Circle.
        
        Args:
            amount: The amount of USDC to mint
            currency: The fiat currency to convert from (e.g., "USD", "EUR")
            chain: The blockchain to mint on (e.g., "ethereum", "polygon", "solana")
            metadata: Optional additional data to attach to the transaction
            
        Returns:
            A StablecoinResult containing the transaction ID and status
            
        Raises:
            ValueError: If the mint operation fails
        """
        try:
            # Generate a unique idempotency key
            idempotency_key = str(uuid.uuid4())
            
            # Prepare the mint request
            mint_request = {
                "amount": str(amount),  # Convert to string as required by Circle API
                "currency": currency.upper(),
                "chain": chain.lower(),
                "idempotencyKey": idempotency_key
            }
            
            # Add metadata if provided
            if metadata:
                mint_request["metadata"] = metadata
            
            # Execute the mint operation with retry logic
            response = await self._execute_with_retry(
                "mint_usdc", 
                self.client.mint_usdc,
                mint_request
            )
            
            # Extract response data
            tx_id = response.get("id", "unknown")
            status = self._map_status(response.get("status", "pending"))
            settled_at = self._parse_datetime(response.get("createdAt"))
            
            return CircleStablecoinResult(
                tx_id=tx_id,
                status=status,
                settled_at=settled_at
            )
            
        except ValueError as e:
            # Re-raise ValueError with more context
            logger.error(f"USDC minting failed: {str(e)}")
            raise
        except Exception as e:
            # Convert other exceptions to ValueError
            logger.error(f"Unexpected error during USDC minting: {str(e)}")
            raise ValueError(f"Failed to mint USDC: {str(e)}")
    
    async def redeem(
        self, 
        amount: float, 
        currency: str, 
        bank_account_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> StablecoinResult:
        """
        Redeem USDC stablecoins for fiat currency through Circle.
        
        Args:
            amount: The amount of USDC to redeem
            currency: The fiat currency to receive (e.g., "USD", "EUR")
            bank_account_id: The ID of the bank account to send the fiat currency to
            metadata: Optional additional data to attach to the transaction
            
        Returns:
            A StablecoinResult containing the transaction ID and status
            
        Raises:
            ValueError: If the redemption operation fails
        """
        try:
            # Generate a unique idempotency key
            idempotency_key = str(uuid.uuid4())
            
            # Prepare the redemption request
            redeem_request = {
                "amount": str(amount),  # Convert to string as required by Circle API
                "currency": currency.upper(),
                "bankAccountId": bank_account_id,
                "idempotencyKey": idempotency_key
            }
            
            # Add metadata if provided
            if metadata:
                redeem_request["metadata"] = metadata
            
            # Execute the redemption operation with retry logic
            response = await self._execute_with_retry(
                "redeem_usdc", 
                self.client.redeem_usdc,
                redeem_request
            )
            
            # Extract response data
            tx_id = response.get("id", "unknown")
            status = self._map_status(response.get("status", "pending"))
            settled_at = self._parse_datetime(response.get("createdAt"))
            
            return CircleStablecoinResult(
                tx_id=tx_id,
                status=status,
                settled_at=settled_at
            )
            
        except ValueError as e:
            # Re-raise ValueError with more context
            logger.error(f"USDC redemption failed: {str(e)}")
            raise
        except Exception as e:
            # Convert other exceptions to ValueError
            logger.error(f"Unexpected error during USDC redemption: {str(e)}")
            raise ValueError(f"Failed to redeem USDC: {str(e)}")
    
    async def get_balance(
        self,
        wallet_address: str,
        chain: Optional[str] = None
    ) -> float:
        """
        Get the USDC balance for a wallet address.
        
        Args:
            wallet_address: The blockchain wallet address to check
            chain: Optional blockchain to check (if None, checks the default chain)
            
        Returns:
            The USDC balance as a float
            
        Raises:
            ValueError: If the balance check fails
        """
        try:
            # Prepare the balance request
            balance_request = {
                "address": wallet_address
            }
            
            # Add chain if specified
            if chain:
                balance_request["chain"] = chain.lower()
            
            # Execute the balance check operation with retry logic
            response = await self._execute_with_retry(
                "get_balance", 
                self.client.get_wallet_balance,
                balance_request
            )
            
            # Extract balance data
            balance = 0.0
            balances = response.get("balances", [])
            
            # Find USDC balance
            for asset in balances:
                if asset.get("token", "").upper() == "USDC":
                    try:
                        balance = float(asset.get("amount", "0"))
                    except (ValueError, TypeError):
                        balance = 0.0
                    break
            
            return balance
            
        except ValueError as e:
            # Re-raise ValueError with more context
            logger.error(f"USDC balance check failed: {str(e)}")
            raise
        except Exception as e:
            # Convert other exceptions to ValueError
            logger.error(f"Unexpected error during USDC balance check: {str(e)}")
            raise ValueError(f"Failed to check USDC balance: {str(e)}")
    
    async def get_transaction_status(
        self,
        tx_id: str
    ) -> str:
        """
        Get the current status of a Circle transaction.
        
        Args:
            tx_id: The transaction ID to check
            
        Returns:
            The status of the transaction (e.g., "pending", "completed", "failed")
            
        Raises:
            ValueError: If the transaction status check fails
        """
        try:
            # Execute the transaction status check with retry logic
            response = await self._execute_with_retry(
                "get_transaction", 
                self.client.get_transaction,
                tx_id
            )
            
            # Extract and map status
            circle_status = response.get("status", "unknown")
            return self._map_status(circle_status)
            
        except ValueError as e:
            # Re-raise ValueError with more context
            logger.error(f"Transaction status check failed: {str(e)}")
            raise
        except Exception as e:
            # Convert other exceptions to ValueError
            logger.error(f"Unexpected error during transaction status check: {str(e)}")
            raise ValueError(f"Failed to check transaction status: {str(e)}")
            
    async def get_supported_chains(self) -> List[str]:
        """
        Get the list of blockchain networks supported by Circle.
        
        Returns:
            A list of supported blockchain identifiers
            
        Raises:
            ValueError: If the operation fails
        """
        try:
            # Execute the supported chains check with retry logic
            response = await self._execute_with_retry(
                "get_supported_chains", 
                self.client.get_supported_chains,
            )
            
            # Extract chains data
            chains = response.get("chains", [])
            return [chain.get("id") for chain in chains]
            
        except ValueError as e:
            # Re-raise ValueError with more context
            logger.error(f"Supported chains check failed: {str(e)}")
            raise
        except Exception as e:
            # Convert other exceptions to ValueError
            logger.error(f"Unexpected error during supported chains check: {str(e)}")
            raise ValueError(f"Failed to get supported chains: {str(e)}")
            
    async def get_transaction_history(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        page_size: int = 50,
        page_number: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get transaction history for USDC operations.
        
        Args:
            from_date: Optional start date for filtering transactions
            to_date: Optional end date for filtering transactions
            page_size: Number of transactions per page (max 100)
            page_number: Page number to retrieve
            
        Returns:
            A list of transaction records
            
        Raises:
            ValueError: If the operation fails
        """
        try:
            # Prepare the request
            history_request = {
                "pageSize": min(page_size, 100),  # Max 100 per Circle API docs
                "pageNumber": page_number
            }
            
            # Add date filters if specified
            if from_date:
                history_request["from"] = from_date.isoformat()
            if to_date:
                history_request["to"] = to_date.isoformat()
            
            # Execute the transaction history check with retry logic
            response = await self._execute_with_retry(
                "get_transaction_history", 
                self.client.get_transaction_history,
                history_request
            )
            
            # Extract transactions data
            return response.get("items", [])
            
        except ValueError as e:
            # Re-raise ValueError with more context
            logger.error(f"Transaction history check failed: {str(e)}")
            raise
        except Exception as e:
            # Convert other exceptions to ValueError
            logger.error(f"Unexpected error during transaction history check: {str(e)}")
            raise ValueError(f"Failed to get transaction history: {str(e)}") 