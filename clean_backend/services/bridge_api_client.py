"""
Bridge API integration for multi-chain crypto payment system
Combines all advanced and basic features for maximum functionality and compatibility
Roj you dont need this if you have the JSON file 
"""

import aiohttp
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
import time
from datetime import datetime, timedelta
import hashlib
import hmac
import re

logger = logging.getLogger(__name__)

# Data class
class PaymentRail(Enum):
    # Fiat Rails
    ACH = "ach"
    WIRE = "wire"
    SEPA = "sepa"
    SPEI = "spei"
    SWIFT = "swift"
    
    # Crypto Rails
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BASE = "base"
    SOLANA = "solana"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    
    # Special Rails
    FIAT_DEPOSIT_RETURN = "fiat_deposit_return"
    CRYPTO_DEPOSIT_RETURN = "crypto_deposit_return"

class BridgeTransferStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class TransferType(Enum):
    ON_RAMP = "on_ramp"  # Fiat to crypto
    OFF_RAMP = "off_ramp"  # Crypto to fiat
    CRYPTO_TO_CRYPTO = "crypto_to_crypto"
    FIAT_TO_FIAT = "fiat_to_fiat"

@dataclass
class BridgeTransferRequest:
    amount: str
    source_network: str
    source_address: str
    destination_network: str
    destination_address: str
    currency: str = "usdc"
    urgency: str = "low"
    metadata: Dict[str, Any] = None
    # Enhanced fields
    on_behalf_of: Optional[str] = None
    source: Optional[Dict[str, Any]] = None
    destination: Optional[Dict[str, Any]] = None
    developer_fee: Optional[str] = None
    developer_fee_percent: Optional[str] = None
    idempotency_key: Optional[str] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class BridgeTransferResponse:
    transfer_id: str
    status: BridgeTransferStatus
    amount: str
    source_network: str
    destination_network: str
    estimated_fee: str
    estimated_time: int  # seconds
    created_at: datetime
    expires_at: datetime
    # Enhanced fields
    id: Optional[str] = None
    currency: Optional[str] = None
    source: Optional[Dict[str, Any]] = None
    destination: Optional[Dict[str, Any]] = None
    updated_at: Optional[datetime] = None
    source_deposit_instructions: Optional[Dict[str, Any]] = None
    destination_deposit_instructions: Optional[Dict[str, Any]] = None
    transaction_hash: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class ExternalAccount:
    id: str
    type: str
    currency: str
    account_number: Optional[str] = None
    routing_number: Optional[str] = None
    iban: Optional[str] = None
    swift_code: Optional[str] = None
    bank_name: Optional[str] = None
    account_holder_name: Optional[str] = None
    status: str = "pending"
    created_at: datetime = None


class BridgeError(Exception):
    """Bridge API error"""
    def __init__(self, message: str, error_code: str, details: Dict[str, Any] = None, status_code: int = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)

class BridgeAPIError(Exception):
    def __init__(self, message: str, status_code: int, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

# main
class BridgeAPIClient:
    """
    Unified Bridge API client with comprehensive features
    """
    
    def __init__(self, api_key: str = None, base_url: str = "https://api.bridge.xyz", timeout: int = 30):
        # Allow caller to omit api_key; fall back to central settings.
        if api_key is None:
            try:
                from clean_backend.config.settings import settings as _settings  # local import to avoid circulars
                api_key = _settings.bridge_api_key.get_secret_value()
            except Exception:  # pragma: no cover
                api_key = None

        self.api_key = api_key
        if not self.api_key:
            raise ValueError("Bridge API key is required – set BRIDGE_API_KEY env var or pass explicitly")
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = None
        self.retry_attempts = 3
        self.retry_delay = 1
        
        # Rate limiting
        self.rate_limits = {
            "requests_per_minute": 100,
            "requests_per_hour": 1000,
            "requests_per_day": 10000
        }
        
        # Supported networks (enhanced)
        self.supported_networks = {
            "ethereum": {
                "name": "Ethereum",
                "chain_id": 1,
                "currency": "ETH",
                "usdc_contract": "0xA0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
                "rail": PaymentRail.ETHEREUM
            },
            "polygon": {
                "name": "Polygon",
                "chain_id": 137,
                "currency": "MATIC",
                "usdc_contract": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
                "rail": PaymentRail.POLYGON
            },
            "base": {
                "name": "Base",
                "chain_id": 8453,
                "currency": "ETH",
                "usdc_contract": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                "rail": PaymentRail.BASE
            },
            "solana": {
                "name": "Solana",
                "chain_id": "solana:mainnet",
                "currency": "SOL",
                "usdc_contract": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                "rail": PaymentRail.SOLANA
            }
        }
        
        # Supported payment rails
        self.supported_rails = {
            "fiat": [PaymentRail.ACH, PaymentRail.WIRE, PaymentRail.SEPA, PaymentRail.SPEI, PaymentRail.SWIFT],
            "crypto": [PaymentRail.ETHEREUM, PaymentRail.POLYGON, PaymentRail.BASE, PaymentRail.SOLANA, PaymentRail.ARBITRUM, PaymentRail.OPTIMISM]
        }
        
        # Compliance thresholds
        self.compliance_thresholds = {
            "kyc_required": 1000,  # USD
            "aml_threshold": 3000,  # USD
            "ctr_threshold": 10000,  # USD
            "sar_threshold": 5000,   # USD
        }

    async def __aenter__(self):
        """Async context manager entry"""
        await self._create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._close_session()

    async def _create_session(self):
        """Create HTTP session with connection pooling"""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=20,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            timeout = aiohttp.ClientTimeout(total=self.timeout, connect=10)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    "Api-Key": self.api_key,
                    "Content-Type": "application/json",
                    "User-Agent": "Liquicity-Bridge-Client/1.0"
                }
            )

    async def _close_session(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session (for backward compatibility)"""
        if self.session is None or self.session.closed:
            await self._create_session()
        return self.session

    async def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None, retry_count: int = 0) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic and error handling
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, json=data) as response:
                response_data = await response.json()
                
                if response.status >= 400:
                    error_message = response_data.get("message", "Unknown error")
                    error_code = response_data.get("code", "UNKNOWN_ERROR")
                    raise BridgeAPIError(error_message, response.status, error_code, response_data)
                
                return response_data
                
        except aiohttp.ClientError as e:
            if retry_count < self.retry_attempts:
                await asyncio.sleep(self.retry_delay * (2 ** retry_count))
                return await self._make_request(method, endpoint, data, retry_count + 1)
            raise BridgeError(f"Network error: {str(e)}", "NETWORK_ERROR")
        
        except BridgeAPIError as e:
            raise BridgeError(e.message, e.error_code or "API_ERROR", e.details, e.status_code)
        except Exception as e:
            raise BridgeError(f"Unexpected error: {str(e)}", "UNEXPECTED_ERROR")

    def _generate_idempotency_key(self, data: Dict[str, Any]) -> str:
        """Generate idempotency key for request"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _validate_address(self, address: str, network: str) -> bool:
        """Validate address format for network"""
        if not address:
            return False
        
        if network in ["ethereum", "polygon", "base", "arbitrum", "optimism"]:
            # EVM address validation
            return bool(re.match(r"^0x[a-fA-F0-9]{40}$", address))
        elif network == "solana":
            # Solana address validation
            return bool(re.match(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$", address))
        
        return False
    
    def _validate_network(self, network: str) -> bool:
        """Validate network support"""
        return network in self.supported_networks

    # --- CORE TRANSFER METHODS (Backward Compatible) ---
    async def create_transfer(self, request: BridgeTransferRequest) -> BridgeTransferResponse:
        """
        Create a new bridge transfer using the real Bridge API.
        """
        if not self._validate_network(request.source_network):
            raise BridgeError(f"Unsupported source network: {request.source_network}", "UNSUPPORTED_NETWORK")
        if not self._validate_network(request.destination_network):
            raise BridgeError(f"Unsupported destination network: {request.destination_network}", "UNSUPPORTED_NETWORK")
        if not self._validate_address(request.source_address, request.source_network):
            raise BridgeError(f"Invalid source address: {request.source_address}", "INVALID_ADDRESS")
        if not self._validate_address(request.destination_address, request.destination_network):
            raise BridgeError(f"Invalid destination address: {request.destination_address}", "INVALID_ADDRESS")
        
        # Prepare transfer data
        transfer_data = {
            "amount": request.amount,
            "source_network": request.source_network,
            "source_address": request.source_address,
            "destination_network": request.destination_network,
            "destination_address": request.destination_address,
            "currency": request.currency,
            "urgency": request.urgency,
            "metadata": request.metadata
        }
        
        # Add enhanced fields if available
        if request.on_behalf_of:
            transfer_data["on_behalf_of"] = request.on_behalf_of
        if request.source:
            transfer_data["source"] = request.source
        if request.destination:
            transfer_data["destination"] = request.destination
        if request.developer_fee:
            transfer_data["developer_fee"] = request.developer_fee
        if request.developer_fee_percent:
            transfer_data["developer_fee_percent"] = request.developer_fee_percent
        if request.idempotency_key:
            transfer_data["idempotency_key"] = request.idempotency_key
        else:
            transfer_data["idempotency_key"] = self._generate_idempotency_key(transfer_data)
        
        try:
            resp_json = await self._make_request("POST", "/v0/transfers", transfer_data)
            return self._parse_transfer_response(resp_json)
        except BridgeError:
            raise
        except Exception as e:
            raise BridgeError(f"Failed to create transfer: {str(e)}", "TRANSFER_CREATION_FAILED")

    async def get_transfer_status(self, transfer_id: str) -> BridgeTransferResponse:
        """
        Get transfer status from the real Bridge API.
        """
        try:
            resp_json = await self._make_request("GET", f"/v0/transfers/{transfer_id}")
            return self._parse_transfer_response(resp_json)
        except BridgeError:
            raise
        except Exception as e:
            raise BridgeError(f"Failed to get transfer status: {str(e)}", "TRANSFER_STATUS_FAILED")

    async def get_supported_networks(self) -> Dict[str, Dict[str, Any]]:
        """
        Get supported networks (local config, or fetch from Bridge API if available).
        """
        return self.supported_networks

    async def estimate_fee(self, source_network: str, destination_network: str, amount: str) -> Dict[str, Any]:
        """
        Estimate transfer fee using the real Bridge API.
        """
        if not self._validate_network(source_network):
            raise BridgeError(f"Unsupported source network: {source_network}", "UNSUPPORTED_NETWORK")
        if not self._validate_network(destination_network):
            raise BridgeError(f"Unsupported destination network: {destination_network}", "UNSUPPORTED_NETWORK")
        
        payload = {
            "source_network": source_network,
            "destination_network": destination_network,
            "amount": amount
        }
        
        try:
            return await self._make_request("POST", "/v0/fees/estimate", payload)
        except BridgeError:
            raise
        except Exception as e:
            raise BridgeError(f"Failed to estimate fee: {str(e)}", "FEE_ESTIMATION_FAILED")

    async def get_transfer_history(self, address: str, network: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get transfer history for an address using the real Bridge API.
        """
        if not self._validate_network(network):
            raise BridgeError(f"Unsupported network: {network}", "UNSUPPORTED_NETWORK")
        
        params = {"address": address, "network": network, "limit": limit}
        
        try:
            return await self._make_request("GET", "/v0/transfers/history", params=params)
        except BridgeError:
            raise
        except Exception as e:
            raise BridgeError(f"Failed to get transfer history: {str(e)}", "HISTORY_FETCH_FAILED")

    # --- ENHANCED METHODS ---
    async def list_transfers(self, limit: int = 100, offset: int = 0, status: Optional[BridgeTransferStatus] = None) -> List[BridgeTransferResponse]:
        """List all transfers with optional filtering"""
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status.value
        
        try:
            resp_json = await self._make_request("GET", "/v0/transfers", params=params)
            return [self._parse_transfer_response(transfer) for transfer in resp_json.get("transfers", [])]
        except BridgeError:
            raise
        except Exception as e:
            raise BridgeError(f"Failed to list transfers: {str(e)}", "TRANSFER_LIST_FAILED")

    async def cancel_transfer(self, transfer_id: str) -> BridgeTransferResponse:
        """Cancel a pending transfer"""
        try:
            resp_json = await self._make_request("POST", f"/v0/transfers/{transfer_id}/cancel")
            return self._parse_transfer_response(resp_json)
        except BridgeError:
            raise
        except Exception as e:
            raise BridgeError(f"Failed to cancel transfer: {str(e)}", "TRANSFER_CANCELLATION_FAILED")

    async def create_external_account(self, account_data: Dict[str, Any]) -> ExternalAccount:
        """Create external bank account"""
        try:
            resp_json = await self._make_request("POST", "/v0/external_accounts", account_data)
            return self._parse_external_account_response(resp_json)
        except BridgeError:
            raise
        except Exception as e:
            raise BridgeError(f"Failed to create external account: {str(e)}", "ACCOUNT_CREATION_FAILED")

    async def get_external_account(self, account_id: str) -> ExternalAccount:
        """Get external account details"""
        try:
            resp_json = await self._make_request("GET", f"/v0/external_accounts/{account_id}")
            return self._parse_external_account_response(resp_json)
        except BridgeError:
            raise
        except Exception as e:
            raise BridgeError(f"Failed to get external account: {str(e)}", "ACCOUNT_FETCH_FAILED")

    async def list_external_accounts(self, limit: int = 100, offset: int = 0) -> List[ExternalAccount]:
        """List external accounts"""
        params = {"limit": limit, "offset": offset}
        try:
            resp_json = await self._make_request("GET", "/v0/external_accounts", params=params)
            return [self._parse_external_account_response(account) for account in resp_json.get("accounts", [])]
        except BridgeError:
            raise
        except Exception as e:
            raise BridgeError(f"Failed to list external accounts: {str(e)}", "ACCOUNT_LIST_FAILED")

    async def get_supported_rails(self) -> Dict[str, List[str]]:
        """Get supported payment rails"""
        return {
            "fiat": [rail.value for rail in self.supported_rails["fiat"]],
            "crypto": [rail.value for rail in self.supported_rails["crypto"]]
        }

    async def get_exchange_rates(self, base_currency: str = "USD") -> Dict[str, Any]:
        """Get current exchange rates"""
        try:
            return await self._make_request("GET", f"/v0/exchange_rates?base={base_currency}")
        except BridgeError:
            raise
        except Exception as e:
            raise BridgeError(f"Failed to get exchange rates: {str(e)}", "RATES_FETCH_FAILED")

    async def validate_address(self, address: str, rail: PaymentRail) -> Dict[str, Any]:
        """Validate address for specific rail"""
        try:
            return await self._make_request("POST", "/v0/validate_address", {"address": address, "rail": rail.value})
        except BridgeError:
            raise
        except Exception as e:
            raise BridgeError(f"Failed to validate address: {str(e)}", "ADDRESS_VALIDATION_FAILED")

    async def batch_create_transfers(self, transfers: List[BridgeTransferRequest]) -> List[BridgeTransferResponse]:
        """Create multiple transfers in batch"""
        transfer_data = []
        for transfer in transfers:
            data = {
                "amount": transfer.amount,
                "source_network": transfer.source_network,
                "source_address": transfer.source_address,
                "destination_network": transfer.destination_network,
                "destination_address": transfer.destination_address,
                "currency": transfer.currency,
                "urgency": transfer.urgency,
                "metadata": transfer.metadata
            }
            if transfer.on_behalf_of:
                data["on_behalf_of"] = transfer.on_behalf_of
            if transfer.idempotency_key:
                data["idempotency_key"] = transfer.idempotency_key
            else:
                data["idempotency_key"] = self._generate_idempotency_key(data)
            transfer_data.append(data)
        
        try:
            resp_json = await self._make_request("POST", "/v0/transfers/batch", {"transfers": transfer_data})
            return [self._parse_transfer_response(transfer) for transfer in resp_json.get("transfers", [])]
        except BridgeError:
            raise
        except Exception as e:
            raise BridgeError(f"Failed to create batch transfers: {str(e)}", "BATCH_TRANSFER_FAILED")

    # --- HELPER METHODS ---
    def _parse_transfer_response(self, data: Dict[str, Any]) -> BridgeTransferResponse:
        """Parse transfer response from API"""
        return BridgeTransferResponse(
            transfer_id=data.get("transfer_id") or data.get("id", ""),
            status=BridgeTransferStatus(data.get("status", "pending")),
            amount=data.get("amount", "0"),
            source_network=data.get("source_network", ""),
            destination_network=data.get("destination_network", ""),
            estimated_fee=data.get("estimated_fee", "0"),
            estimated_time=data.get("estimated_time", 0),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat())),
            expires_at=datetime.fromisoformat(data.get("expires_at", (datetime.utcnow() + timedelta(hours=1)).isoformat())),
            # Enhanced fields
            id=data.get("id"),
            currency=data.get("currency"),
            source=data.get("source"),
            destination=data.get("destination"),
            updated_at=datetime.fromisoformat(data.get("updated_at")) if data.get("updated_at") else None,
            source_deposit_instructions=data.get("source_deposit_instructions"),
            destination_deposit_instructions=data.get("destination_deposit_instructions"),
            transaction_hash=data.get("transaction_hash"),
            error_message=data.get("error_message")
        )

    def _parse_external_account_response(self, data: Dict[str, Any]) -> ExternalAccount:
        """Parse external account response from API"""
        return ExternalAccount(
            id=data.get("id", ""),
            type=data.get("type", ""),
            currency=data.get("currency", ""),
            account_number=data.get("account_number"),
            routing_number=data.get("routing_number"),
            iban=data.get("iban"),
            swift_code=data.get("swift_code"),
            bank_name=data.get("bank_name"),
            account_holder_name=data.get("account_holder_name"),
            status=data.get("status", "pending"),
            created_at=datetime.fromisoformat(data.get("created_at")) if data.get("created_at") else datetime.utcnow()
        )

    # --- CONVENIENCE METHODS ---
    def create_usdc_transfer_request(
        self,
        amount: str,
        user_id: str,
        source_network: str,
        source_address: str,
        destination_network: str,
        destination_address: str,
        currency: str = "usdc"
    ) -> BridgeTransferRequest:
        """Create USDC transfer request"""
        return BridgeTransferRequest(
            amount=amount,
            source_network=source_network,
            source_address=source_address,
            destination_network=destination_network,
            destination_address=destination_address,
            currency=currency,
            on_behalf_of=user_id,
            metadata={"user_id": user_id, "transfer_type": "usdc"}
        )

    async def close(self):
        """Close the client session"""
        await self._close_session() 