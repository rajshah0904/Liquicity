import os
import uuid
import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Literal, Union

from modern_treasury import ModernTreasury
from modern_treasury.errors import APIStatusError, APIConnectionError, APITimeoutError

from app.payments.providers.base import PaymentProvider, BankAccount, TransactionResult

logger = logging.getLogger(__name__)

# US-specific payment rail types
USPaymentRailType = Literal["ach", "wire", "rtp", "fednow"]

class MTTransactionResult:
    """Implementation of TransactionResult for Modern Treasury"""
    
    def __init__(self, transaction_id: str, status: str, settled_at: Optional[datetime] = None, rail_used: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        self.id = transaction_id
        self.status = status
        self.settled_at = settled_at or datetime.now(timezone.utc)
        self.rail_used = rail_used
        self.metadata = metadata or {}

class USBankAccount:
    """US-specific bank account implementation that validates US routing and account numbers"""
    
    def __init__(self, routing_number: str, account_number: str, account_type: str = "checking"):
        self.country_code = "US"
        self._validate_routing_number(routing_number)
        self._validate_account_number(account_number)
        self.routing_number = routing_number
        self.account_number = account_number
        self.account_type = account_type  # checking, savings
        
    def _validate_routing_number(self, routing_number: str) -> None:
        """Validate US ACH routing number using the checksum algorithm"""
        if not re.match(r'^\d{9}$', routing_number):
            raise ValueError("US routing number must be exactly 9 digits")
        
        # Apply ABA routing number checksum algorithm
        digits = [int(d) for d in routing_number]
        checksum = (
            3 * (digits[0] + digits[3] + digits[6]) +
            7 * (digits[1] + digits[4] + digits[7]) +
            (digits[2] + digits[5] + digits[8])
        )
        
        if checksum % 10 != 0:
            raise ValueError("Invalid US routing number checksum")
    
    def _validate_account_number(self, account_number: str) -> None:
        """Basic validation for US bank account numbers"""
        if not re.match(r'^\d{4,17}$', account_number):
            raise ValueError("US account number must be between 4 and 17 digits")

class ModernTreasuryProvider(PaymentProvider):
    """Modern Treasury payment provider implementation for US payment rails"""
    
    def __init__(self):
        self.client = ModernTreasury(
            api_key=os.getenv("MODERN_TREASURY_API_KEY"),
            organization_id=os.getenv("MODERN_TREASURY_ORG_ID")
        )
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        self.default_originating_account_id = os.getenv("MODERN_TREASURY_DEFAULT_ACCOUNT_ID")
        
        # Rail-specific configurations
        self.rail_configs = {
            "ach": {"default_class": "standard"},  # standard, same_day
            "wire": {"default_priority": "high"},  # high, normal
            "rtp": {},
            "fednow": {}
        }
    
    async def pull(self, amount: float, currency: str, account: BankAccount, 
                   preferred_rail: USPaymentRailType = "ach", 
                   metadata: Optional[Dict[str, Any]] = None) -> TransactionResult:
        """
        Pull funds from a US bank account
        
        Args:
            amount: Amount to pull in dollars
            currency: Currency code (USD for US rails)
            account: Bank account to pull from
            preferred_rail: Preferred payment rail (ach, rtp, fednow)
            metadata: Additional metadata to attach to the transaction
            
        Returns:
            Transaction result with status and details
        """
        if currency.upper() != "USD":
            raise ValueError("US payment rails only support USD currency")
        
        # Validate account is a US account
        if getattr(account, "country_code", "US") != "US":
            raise ValueError("US payment rails require a US bank account")
            
        idempotency_key = str(uuid.uuid4())
        amount_in_cents = int(amount * 100)
        
        # Default to ACH for pull transactions
        payment_rail = preferred_rail if preferred_rail in ["ach"] else "ach"
        
        payment_params = {
            "type": payment_rail,
            "amount": amount_in_cents,
            "currency": "USD",
            "direction": "debit",
            "originating_account_id": self.default_originating_account_id,
            "receiving_account": {
                "account_type": getattr(account, "account_type", "checking"),
                "routing_number": account.routing_number,
                "account_number": account.account_number,
                "country": "US"
            },
            "description": f"{payment_rail.upper()} debit of ${amount:.2f}",
        }
        
        # Add ACH-specific parameters
        if payment_rail == "ach":
            payment_params["ach_class"] = self.rail_configs["ach"]["default_class"]
        
        # Add metadata if provided
        if metadata:
            payment_params["metadata"] = metadata
            
        return await self._execute_with_retry(
            "payment_order", 
            payment_params, 
            idempotency_key
        )
    
    async def push(self, amount: float, currency: str, account: BankAccount, 
                  preferred_rail: USPaymentRailType = "rtp",
                  fallback_hierarchy: Optional[list[USPaymentRailType]] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> TransactionResult:
        """
        Push funds to a US bank account with smart rail selection and fallback
        
        Args:
            amount: Amount to push in dollars
            currency: Currency code (USD for US rails)
            account: Bank account to push to
            preferred_rail: Preferred payment rail (rtp, ach, wire, fednow)
            fallback_hierarchy: Ordered list of fallback rails if preferred fails
            metadata: Additional metadata to attach to the transaction
            
        Returns:
            Transaction result with status and details
        """
        if currency.upper() != "USD":
            raise ValueError("US payment rails only support USD currency")
            
        # Validate account is a US account
        if getattr(account, "country_code", "US") != "US":
            raise ValueError("US payment rails require a US bank account")
            
        idempotency_key = str(uuid.uuid4())
        amount_in_cents = int(amount * 100)
        
        # Setup fallback hierarchy if not provided
        if not fallback_hierarchy:
            if preferred_rail == "rtp":
                fallback_hierarchy = ["fednow", "ach", "wire"]
            elif preferred_rail == "fednow":
                fallback_hierarchy = ["rtp", "ach", "wire"]
            elif preferred_rail == "ach":
                fallback_hierarchy = ["rtp", "fednow", "wire"]
            else:  # wire
                fallback_hierarchy = ["rtp", "fednow", "ach"]
        
        # Try preferred rail first, then fallbacks
        rails_to_try = [preferred_rail] + fallback_hierarchy
        last_error = None
        
        for rail in rails_to_try:
            try:
                payment_params = {
                    "type": rail,
                    "amount": amount_in_cents,
                    "currency": "USD",
                    "direction": "credit",
                    "originating_account_id": self.default_originating_account_id,
                    "receiving_account": {
                        "account_type": getattr(account, "account_type", "checking"),
                        "routing_number": account.routing_number,
                        "account_number": account.account_number,
                        "country": "US"
                    },
                    "description": f"{rail.upper()} credit of ${amount:.2f}"
                }
                
                # Add rail-specific parameters
                if rail == "ach":
                    # For smaller amounts, use same-day ACH
                    if amount <= 25000:
                        payment_params["ach_class"] = "same_day"
                    else:
                        payment_params["ach_class"] = "standard"
                elif rail == "wire":
                    payment_params["priority"] = self.rail_configs["wire"]["default_priority"]
                
                # Add metadata
                if metadata:
                    payment_params["metadata"] = metadata
                    
                # Add the rail used to metadata
                if not payment_params.get("metadata"):
                    payment_params["metadata"] = {}
                payment_params["metadata"]["rail_used"] = rail
                
                # Generate a unique idempotency key for each rail attempt
                current_idempotency_key = f"{idempotency_key}-{rail}"
                
                result = await self._execute_with_retry(
                    "payment_order", 
                    payment_params, 
                    current_idempotency_key
                )
                
                # Set the rail used in the result
                if isinstance(result, MTTransactionResult):
                    result.rail_used = rail
                
                return result
                
            except APIStatusError as e:
                logger.warning(f"{rail.upper()} transfer failed: {str(e)}. Trying next rail.")
                last_error = e
                continue
        
        # If we get here, all rails failed
        if last_error:
            logger.error(f"All payment rails failed. Last error: {str(last_error)}")
            raise last_error
        else:
            raise ValueError("Unable to process payment through any available rail")
    
    async def wire_transfer(self, amount: float, account: BankAccount, 
                           beneficiary_name: str,
                           memo: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> TransactionResult:
        """
        Send a wire transfer to a US bank account
        
        Args:
            amount: Amount to send in dollars
            account: Bank account to send to
            beneficiary_name: Name of the beneficiary
            memo: Optional memo to include with the wire
            metadata: Additional metadata to attach to the transaction
            
        Returns:
            Transaction result with status and details
        """
        idempotency_key = str(uuid.uuid4())
        amount_in_cents = int(amount * 100)
        
        payment_params = {
            "type": "wire",
            "amount": amount_in_cents,
            "currency": "USD",
            "direction": "credit",
            "originating_account_id": self.default_originating_account_id,
            "receiving_account": {
                "account_type": getattr(account, "account_type", "checking"),
                "routing_number": account.routing_number,
                "account_number": account.account_number,
                "country": "US",
                "name": beneficiary_name
            },
            "priority": self.rail_configs["wire"]["default_priority"],
            "description": f"Wire transfer of ${amount:.2f}",
        }
        
        if memo:
            payment_params["originator_to_beneficiary_information"] = memo
            
        # Add metadata if provided
        if metadata:
            payment_params["metadata"] = metadata
        
        return await self._execute_with_retry(
            "payment_order", 
            payment_params, 
            idempotency_key
        )
    
    async def same_day_ach(self, amount: float, account: BankAccount,
                          is_push: bool = True,
                          metadata: Optional[Dict[str, Any]] = None) -> TransactionResult:
        """
        Send a same-day ACH transfer (only works for amounts <= $25,000)
        
        Args:
            amount: Amount to send in dollars (must be <= $25,000)
            account: Bank account to send to/from
            is_push: Whether this is a push (credit) or pull (debit)
            metadata: Additional metadata to attach to the transaction
            
        Returns:
            Transaction result with status and details
        """
        if amount > 25000:
            raise ValueError("Same-day ACH is limited to $25,000 per transaction")
            
        idempotency_key = str(uuid.uuid4())
        amount_in_cents = int(amount * 100)
        
        payment_params = {
            "type": "ach",
            "amount": amount_in_cents,
            "currency": "USD",
            "direction": "credit" if is_push else "debit",
            "originating_account_id": self.default_originating_account_id,
            "receiving_account": {
                "account_type": getattr(account, "account_type", "checking"),
                "routing_number": account.routing_number,
                "account_number": account.account_number,
                "country": "US"
            },
            "ach_class": "same_day",
            "description": f"Same-day ACH {'credit' if is_push else 'debit'} of ${amount:.2f}",
        }
        
        # Add metadata if provided
        if metadata:
            payment_params["metadata"] = metadata
            
        return await self._execute_with_retry(
            "payment_order", 
            payment_params, 
            idempotency_key
        )
    
    async def fednow_transfer(self, amount: float, account: BankAccount,
                             metadata: Optional[Dict[str, Any]] = None) -> TransactionResult:
        """
        Send a FedNow instant payment (US Federal Reserve's instant payment system)
        
        Args:
            amount: Amount to send in dollars
            account: Bank account to send to
            metadata: Additional metadata to attach to the transaction
            
        Returns:
            Transaction result with status and details
        """
        idempotency_key = str(uuid.uuid4())
        amount_in_cents = int(amount * 100)
        
        payment_params = {
            "type": "fednow",
            "amount": amount_in_cents,
            "currency": "USD",
            "direction": "credit",
            "originating_account_id": self.default_originating_account_id,
            "receiving_account": {
                "account_type": getattr(account, "account_type", "checking"),
                "routing_number": account.routing_number,
                "account_number": account.account_number,
                "country": "US"
            },
            "description": f"FedNow instant payment of ${amount:.2f}",
        }
        
        # Add metadata if provided
        if metadata:
            payment_params["metadata"] = metadata
            
        return await self._execute_with_retry(
            "payment_order", 
            payment_params, 
            idempotency_key
        )
    
    async def _execute_with_retry(self, method_name: str, params: Dict[str, Any], idempotency_key: str) -> TransactionResult:
        """Execute API call with retry logic"""
        retries = 0
        
        while retries <= self.max_retries:
            try:
                # Add idempotency key to prevent duplicate payments
                headers = {"Idempotency-Key": idempotency_key}
                
                # Execute the API call
                if method_name == "payment_order":
                    response = await asyncio.to_thread(
                        self.client.payment_orders.create,
                        **params,
                        idempotency_key=idempotency_key
                    )
                else:
                    raise ValueError(f"Unsupported method: {method_name}")
                
                # Map status
                status_mapping = {
                    "approved": "pending",
                    "pending": "pending",
                    "completed": "completed",
                    "failed": "failed",
                    "returned": "failed"
                }
                
                status = status_mapping.get(response.status, "pending")
                
                # Extract settled_at if available
                settled_at = None
                if hasattr(response, "effective_date"):
                    settled_at = datetime.fromisoformat(response.effective_date) if response.effective_date else None
                
                # Get the rail used if available in metadata
                rail_used = None
                metadata = {}
                if hasattr(response, "metadata") and response.metadata:
                    metadata = response.metadata
                    rail_used = metadata.get("rail_used")
                
                return MTTransactionResult(
                    transaction_id=response.id,
                    status=status,
                    settled_at=settled_at,
                    rail_used=rail_used,
                    metadata=metadata
                )
                
            except (APIConnectionError, APITimeoutError) as e:
                # These are retryable errors
                retries += 1
                if retries <= self.max_retries:
                    wait_time = self.retry_delay * (2 ** (retries - 1))  # Exponential backoff
                    logger.warning(f"API error: {str(e)}. Retrying in {wait_time}s ({retries}/{self.max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Failed after {self.max_retries} retries: {str(e)}")
                    raise
            except APIStatusError as e:
                # Check if this is a retryable status code
                if e.status_code in [429, 503, 504]:
                    retries += 1
                    if retries <= self.max_retries:
                        wait_time = self.retry_delay * (2 ** (retries - 1))
                        logger.warning(f"API status error {e.status_code}: {str(e)}. Retrying in {wait_time}s ({retries}/{self.max_retries})")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"Failed after {self.max_retries} retries: {str(e)}")
                        raise
                else:
                    # Not retryable status code
                    logger.error(f"API status error {e.status_code}: {str(e)}")
                    raise 