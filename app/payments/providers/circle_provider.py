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

import httpx

from .stablecoin_base import StablecoinProvider, StablecoinResult

logger = logging.getLogger(__name__)

# Exceptions used by CircleProvider and tests
class CircleAPIError(Exception):
    """Raised when Circle API returns a client error"""
    pass

class CircleNetworkError(Exception):
    """Raised when a network error occurs during Circle API calls"""
    pass

class CircleTimeoutError(Exception):
    """Raised when a Circle API request times out"""
    pass

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
        # HTTPX async client for Circle API
        self.base_url = "https://api.circle.com"
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10.0
        )
        # Expose the API key for tests
        self.client.api_key = api_key
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
    
    async def _execute_with_retry(
        self,
        operation_name: str,
        method: str,
        endpoint: str,
        json_data: Optional[dict] = None
    ) -> Dict[str, Any]:
        """
        Execute an HTTP request to Circle API with retry logic.
        """
        retries = 0
        url = endpoint if endpoint.startswith("http") else f"{self.base_url}{endpoint}"
        while True:
            try:
                resp = await self.client.request(method, url, json=json_data)
            except (httpx.TimeoutException, CircleTimeoutError) as e:
                if retries < self.max_retries:
                    retries += 1
                    await asyncio.sleep(self.retry_delay * (2 ** (retries - 1)))
                    continue
                raise CircleTimeoutError(str(e))
            except (httpx.RequestError, CircleNetworkError) as e:
                if retries < self.max_retries:
                    retries += 1
                    await asyncio.sleep(self.retry_delay * (2 ** (retries - 1)))
                    continue
                raise ValueError(f"Failed to {operation_name} after multiple retries")
            # Check HTTP status
            status = resp.status_code
            if 400 <= status < 500:
                err = resp.json()
                msg = err.get("message") or err.get("error", {}).get("message", "")
                raise ValueError(f"Circle API error: {msg}")
            if status >= 500:
                err = resp.json()
                msg = err.get("message") or err.get("error", {}).get("message", "")
                # Mint operations should retry on server errors
                if operation_name.startswith("mint_usdc"):
                    if retries < self.max_retries:
                        retries += 1
                        await asyncio.sleep(self.retry_delay * (2 ** (retries - 1)))
                        continue
                    raise ValueError(f"Failed to {operation_name} after multiple retries")
                # Other operations error immediately
                raise ValueError(f"Circle API error: {msg}")
            return resp.json()
    
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
        payload = {"amount": str(amount), "currency": currency.upper(), "chain": chain.lower()}
        if metadata:
            payload["metadata"] = metadata
        data = await self._execute_with_retry("mint_usdc", "POST", "/v1/stablecoins/mint", payload)
        return CircleStablecoinResult(
            tx_id=data.get("id", "unknown"),
            status=self._map_status(data.get("status", "pending")),
            settled_at=self._parse_datetime(data.get("createdAt"))
        )
    
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
        payload = {"amount": str(amount), "currency": currency.upper(), "bankAccountId": bank_account_id}
        if metadata:
            payload["metadata"] = metadata
        data = await self._execute_with_retry("redeem_usdc", "POST", "/v1/stablecoins/redeem", payload)
        return CircleStablecoinResult(
            tx_id=data.get("id", "unknown"),
            status=self._map_status(data.get("status", "pending")),
            settled_at=self._parse_datetime(data.get("createdAt"))
        )
    
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
        data = await self._execute_with_retry("get_balance", "GET", "/v1/wallets/balance")
        # Extract balance for USDC
        balance = 0.0
        balances = data.get("balances", [])
        for asset in balances:
            if asset.get("token", "").upper() == "USDC":
                try:
                    balance = float(asset.get("amount", "0"))
                except (ValueError, TypeError):
                    balance = 0.0
                break
        return balance
    
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
        data = await self._execute_with_retry("get_transaction_status", "GET", f"/v1/transactions/{tx_id}")
        return self._map_status(data.get("status", "unknown"))
    
    async def get_supported_chains(self) -> List[str]:
        """
        Get the list of blockchain networks supported by Circle.
        
        Returns:
            A list of supported blockchain identifiers
            
        Raises:
            ValueError: If the operation fails
        """
        data = await self._execute_with_retry("get_supported_chains", "GET", "/v1/chains")
        return [chain.get("id") for chain in data.get("chains", [])]
    
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
        data = await self._execute_with_retry("get_transaction_history", "GET", "/v1/transactions")
        return data.get("items", []) 