import os
import uuid
import asyncio
import logging
import time
import hmac
import base64
import hashlib
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Literal, Union, List

import aiohttp
from aiohttp.client_exceptions import ClientError

from app.payments.providers.base import PaymentProvider, BankAccount, TransactionResult

logger = logging.getLogger(__name__)

# Country-specific payment types
SupportedCountries = Literal["CA", "MX", "NG"]
CountryPaymentMethod = Dict[str, str]

class RapydTransactionResult:
    """Implementation of TransactionResult for Rapyd"""
    
    def __init__(self, transaction_id: str, status: str, settled_at: Optional[datetime] = None, country: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        self.id = transaction_id
        self.status = status
        self.settled_at = settled_at or datetime.now(timezone.utc)
        self.country = country
        self.metadata = metadata or {}

class InternationalBankAccount:
    """Bank account implementation with country-specific validation"""
    
    def __init__(self, routing_number: str, account_number: str, country_code: SupportedCountries, account_type: Optional[str] = None, branch_code: Optional[str] = None):
        self.country_code = country_code
        self._validate_country_code(country_code)
        self._validate_account_details(routing_number, account_number, country_code)
        
        self.routing_number = routing_number
        self.account_number = account_number
        self.account_type = account_type
        self.branch_code = branch_code
        
    def _validate_country_code(self, country_code: str) -> None:
        """Validate that the country code is supported"""
        if country_code not in ["CA", "MX", "NG"]:
            raise ValueError(f"Country code {country_code} is not supported. Must be one of: CA, MX, NG")
    
    def _validate_account_details(self, routing_number: str, account_number: str, country_code: str) -> None:
        """Validate account details based on country-specific rules"""
        if country_code == "CA":
            # Canadian routing numbers: 9 digits (3-digit institution code + 5-digit transit number + check digit)
            if not (routing_number and len(routing_number) == 9 and routing_number.isdigit()):
                raise ValueError("Canadian routing number must be 9 digits")
            # Canadian account numbers are typically 7-12 digits
            if not (account_number and 7 <= len(account_number) <= 12 and account_number.isdigit()):
                raise ValueError("Canadian account number must be 7-12 digits")
                
        elif country_code == "MX":
            # CLABE numbers in Mexico are 18 digits
            if not (account_number and len(account_number) == 18 and account_number.isdigit()):
                raise ValueError("Mexican CLABE account number must be 18 digits")
                
        elif country_code == "NG":
            # Nigerian NUBAN account numbers are 10 digits
            if not (account_number and len(account_number) == 10 and account_number.isdigit()):
                raise ValueError("Nigerian NUBAN account number must be 10 digits")

class RapydProvider(PaymentProvider):
    """Rapyd payment provider implementation for international payments in CA, MX, and NG"""
    
    def __init__(self):
        self.access_key = os.getenv("RAPYD_ACCESS_KEY")
        self.secret_key = os.getenv("RAPYD_SECRET_KEY")
        self.base_url = os.getenv("RAPYD_API_URL", "https://sandboxapi.rapyd.net")
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
        # Country to payment method mapping
        self.country_payment_methods = {
            "CA": {
                "pull": "ca_eft_bank_transfer",
                "push": "ca_eft_payout"
            },
            "MX": {
                "pull": "mx_spei_bank_transfer",
                "push": "mx_spei_payout"
            },
            "NG": {
                "pull": "ng_nibss_bank_transfer",
                "push": "ng_nibss_payout"
            }
        }
    
    def _generate_signature(self, http_method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate the necessary authentication headers for Rapyd API requests"""
        if not self.access_key or not self.secret_key:
            raise ValueError("Rapyd API credentials not configured")
            
        salt = uuid.uuid4().hex
        timestamp = str(int(time.time()))
        
        # Convert empty dict to empty string for signature
        body = ""
        if data:
            body = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        
        to_sign = http_method + endpoint + salt + timestamp + self.access_key + self.secret_key + body
        
        h = hmac.new(
            bytes(self.secret_key, 'utf-8'),
            bytes(to_sign, 'utf-8'),
            hashlib.sha256
        )
        
        signature = base64.b64encode(h.digest()).decode('utf-8')
        
        return {
            'access_key': self.access_key,
            'signature': signature,
            'salt': salt,
            'timestamp': timestamp,
            'Content-Type': 'application/json'
        }
    
    async def _make_api_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make API request to Rapyd with retry logic"""
        url = f"{self.base_url}{endpoint}"
        headers = self._generate_signature(method, endpoint, data)
        
        if idempotency_key:
            headers['idempotency'] = idempotency_key
        
        retries = 0
        last_error = None
        
        while retries <= self.max_retries:
            try:
                async with aiohttp.ClientSession() as session:
                    request_kwargs = {
                        'url': url,
                        'headers': headers
                    }
                    
                    if data and method != 'GET':
                        request_kwargs['json'] = data
                    
                    async with session.request(method, **request_kwargs) as response:
                        response_data = await response.json()
                        
                        # Check for API errors
                        if response.status >= 400 or response_data.get('status', {}).get('status') == 'ERROR':
                            error_message = response_data.get('status', {}).get('message', 'Unknown API error')
                            error_code = response_data.get('status', {}).get('response_code', 'unknown')
                            
                            # Handle rate limiting (retry-able)
                            if response.status == 429 or error_code in ['TOO_MANY_REQUESTS', 'SERVICE_UNAVAILABLE']:
                                retries += 1
                                if retries <= self.max_retries:
                                    wait_time = self.retry_delay * (2 ** (retries - 1))  # Exponential backoff
                                    logger.warning(f"Rapyd API rate limit hit: {error_message}. Retrying in {wait_time}s ({retries}/{self.max_retries})")
                                    await asyncio.sleep(wait_time)
                                    continue
                                else:
                                    logger.error(f"Failed after {self.max_retries} retries: Rate limiting")
                                    raise ValueError(f"Rapyd API rate limit exceeded: {error_message}")
                            
                            # Handle server errors (retry-able)
                            if response.status >= 500 or error_code in ['INTERNAL_SERVER_ERROR', 'SERVER_ERROR']:
                                retries += 1
                                if retries <= self.max_retries:
                                    wait_time = self.retry_delay * (2 ** (retries - 1))
                                    logger.warning(f"Rapyd API server error: {error_message}. Retrying in {wait_time}s ({retries}/{self.max_retries})")
                                    await asyncio.sleep(wait_time)
                                    continue
                                else:
                                    logger.error(f"Failed after {self.max_retries} retries: Server error")
                                    raise ValueError(f"Rapyd API server error: {error_message}")
                            
                            # Non-retriable errors
                            logger.error(f"Rapyd API error: {error_code} - {error_message}")
                            raise ValueError(f"Rapyd API error: {error_code} - {error_message}")
                        
                        # Success case
                        return response_data['data']
                        
            except (ClientError, asyncio.TimeoutError) as e:
                last_error = e
                retries += 1
                if retries <= self.max_retries:
                    wait_time = self.retry_delay * (2 ** (retries - 1))
                    logger.warning(f"Network error: {str(e)}. Retrying in {wait_time}s ({retries}/{self.max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Failed after {self.max_retries} retries: {str(e)}")
                    raise ValueError(f"Network error when connecting to Rapyd API: {str(e)}")
        
        # If we get here, all retries failed
        if last_error:
            raise last_error
        else:
            raise ValueError("Unknown error occurred during API request")
    
    def _get_payment_method_for_country(self, country_code: str, operation: Literal["pull", "push"]) -> str:
        """Get the appropriate payment method type for a country"""
        if country_code not in self.country_payment_methods:
            raise ValueError(f"Unsupported country code: {country_code}")
            
        return self.country_payment_methods[country_code][operation]
    
    def _map_status(self, rapyd_status: str) -> str:
        """Map Rapyd status to our standard status values"""
        status_mapping = {
            "CLO": "completed",  # Closed/Completed
            "COD": "completed",  # Completed
            "COM": "completed",  # Completed
            "ACT": "pending",    # Active
            "CAN": "failed",     # Canceled
            "ERR": "failed",     # Error
            "EXP": "failed",     # Expired
            "REJ": "failed",     # Rejected
            "NEW": "pending",    # New
            "PEN": "pending",    # Pending
            "RDY": "pending",    # Ready
            "REQ": "pending",    # Requested
            "PRO": "pending",    # Processing
        }
        
        return status_mapping.get(rapyd_status, "pending")
    
    async def pull(
        self,
        amount: float,
        currency: str,
        account: BankAccount,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TransactionResult:
        """
        Pull funds from an international bank account
        
        Args:
            amount: Amount to pull in local currency
            currency: Currency code (CAD, MXN, NGN)
            account: International bank account to pull from
            metadata: Additional metadata to attach to the transaction
            
        Returns:
            Transaction result with status and details
        """
        # Validate we're using a supported country
        if not hasattr(account, 'country_code') or account.country_code not in ["CA", "MX", "NG"]:
            raise ValueError(f"Unsupported country code: {getattr(account, 'country_code', 'unknown')}")
            
        # Map currencies to expected format for each country
        country_currencies = {
            "CA": "CAD",
            "MX": "MXN",
            "NG": "NGN"
        }
        
        expected_currency = country_currencies[account.country_code]
        if currency.upper() != expected_currency:
            raise ValueError(f"Invalid currency {currency} for country {account.country_code}. Expected {expected_currency}")
        
        idempotency_key = str(uuid.uuid4())
        payment_method = self._get_payment_method_for_country(account.country_code, "pull")
        
        # Prepare beneficiary data based on country
        beneficiary_data = {
            "account_number": account.account_number,
            "routing_number": account.routing_number,
        }
        
        # Add optional parameters if available
        if hasattr(account, 'account_type') and account.account_type:
            beneficiary_data["account_type"] = account.account_type
            
        if hasattr(account, 'branch_code') and account.branch_code:
            beneficiary_data["branch_code"] = account.branch_code
        
        # Prepare request data
        request_data = {
            "amount": amount,
            "currency": currency.upper(),
            "payment_method": payment_method,
            "country": account.country_code,
            "beneficiary": beneficiary_data,
            "description": f"Bank pull of {amount} {currency}",
        }
        
        # Add metadata if provided
        if metadata:
            request_data["metadata"] = metadata
        
        try:
            response = await self._make_api_request(
                "POST",
                "/v1/payments/bank-transfers/collect",
                data=request_data,
                idempotency_key=idempotency_key
            )
            
            # Extract response data
            transaction_id = response.get("id")
            status = self._map_status(response.get("status", "PEN"))
            
            # Try to parse created_at date
            settled_at = None
            if "created_at" in response and response["created_at"]:
                try:
                    # Rapyd uses Unix timestamps
                    if isinstance(response["created_at"], (int, float)):
                        settled_at = datetime.fromtimestamp(response["created_at"], timezone.utc)
                    # Or they might provide a formatted string
                    else:
                        settled_at = datetime.fromisoformat(response["created_at"].replace('Z', '+00:00'))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to parse created_at date: {str(e)}")
            
            return RapydTransactionResult(
                transaction_id=transaction_id,
                status=status,
                settled_at=settled_at,
                country=account.country_code,
                metadata=metadata
            )
            
        except ValueError as e:
            logger.error(f"Pull transaction failed: {str(e)}")
            raise
    
    async def push(
        self,
        amount: float,
        currency: str,
        account: BankAccount,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TransactionResult:
        """
        Push funds to an international bank account
        
        Args:
            amount: Amount to push in local currency
            currency: Currency code (CAD, MXN, NGN)
            account: International bank account to push to
            metadata: Additional metadata to attach to the transaction
            
        Returns:
            Transaction result with status and details
        """
        # Validate we're using a supported country
        if not hasattr(account, 'country_code') or account.country_code not in ["CA", "MX", "NG"]:
            raise ValueError(f"Unsupported country code: {getattr(account, 'country_code', 'unknown')}")
            
        # Map currencies to expected format for each country
        country_currencies = {
            "CA": "CAD",
            "MX": "MXN",
            "NG": "NGN"
        }
        
        expected_currency = country_currencies[account.country_code]
        if currency.upper() != expected_currency:
            raise ValueError(f"Invalid currency {currency} for country {account.country_code}. Expected {expected_currency}")
        
        idempotency_key = str(uuid.uuid4())
        payment_method = self._get_payment_method_for_country(account.country_code, "push")
        
        # Prepare beneficiary data based on country
        beneficiary_data = {
            "account_number": account.account_number,
            "routing_number": account.routing_number,
            "country": account.country_code,
            "currency": currency.upper(),
        }
        
        # Add optional parameters if available
        if hasattr(account, 'account_type') and account.account_type:
            beneficiary_data["account_type"] = account.account_type
            
        if hasattr(account, 'branch_code') and account.branch_code:
            beneficiary_data["branch_code"] = account.branch_code
        
        # Prepare request data
        request_data = {
            "amount": amount,
            "currency": currency.upper(),
            "payout_method_type": payment_method,
            "beneficiary": beneficiary_data,
            "description": f"Bank payout of {amount} {currency}"
        }
        
        # Add metadata if provided
        if metadata:
            request_data["metadata"] = metadata
        
        try:
            response = await self._make_api_request(
                "POST",
                "/v1/payouts",
                data=request_data,
                idempotency_key=idempotency_key
            )
            
            # Extract response data
            transaction_id = response.get("id")
            status = self._map_status(response.get("status", "PEN"))
            
            # Try to parse created_at date
            settled_at = None
            if "created_at" in response and response["created_at"]:
                try:
                    # Rapyd uses Unix timestamps
                    if isinstance(response["created_at"], (int, float)):
                        settled_at = datetime.fromtimestamp(response["created_at"], timezone.utc)
                    # Or they might provide a formatted string
                    else:
                        settled_at = datetime.fromisoformat(response["created_at"].replace('Z', '+00:00'))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to parse created_at date: {str(e)}")
            
            return RapydTransactionResult(
                transaction_id=transaction_id,
                status=status,
                settled_at=settled_at,
                country=account.country_code,
                metadata=metadata
            )
            
        except ValueError as e:
            logger.error(f"Push transaction failed: {str(e)}")
            raise
    
    async def get_transaction_status(self, transaction_id: str) -> str:
        """Get the current status of a transaction"""
        try:
            # First try as a payment
            response = await self._make_api_request(
                "GET",
                f"/v1/payments/{transaction_id}",
            )
            return self._map_status(response.get("status", "unknown"))
        except ValueError:
            try:
                # Then try as a payout
                response = await self._make_api_request(
                    "GET",
                    f"/v1/payouts/{transaction_id}",
                )
                return self._map_status(response.get("status", "unknown"))
            except ValueError as e:
                logger.error(f"Failed to get transaction status: {str(e)}")
                return "unknown"

    async def get_available_payment_methods(self, country_code: SupportedCountries) -> List[Dict[str, Any]]:
        """Get available payment methods for a specific country"""
        try:
            response = await self._make_api_request(
                "GET",
                f"/v1/payment_methods/country?country={country_code}",
            )
            return response
        except ValueError as e:
            logger.error(f"Failed to get payment methods: {str(e)}")
            return [] 