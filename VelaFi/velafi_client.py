"""Async client wrapper for the VelaFi REST API.

Only the public method signatures are implemented at this stage. Logic still will need to be
added 
"""
from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

import aiohttp
from pydantic import BaseModel, Field

_logger = logging.getLogger(__name__)



# Pydantic models – request / response stubs 

class PaymentMethod(BaseModel):
    id: str
    fiat_rail: str
    country: str
    currency: str
    raw: Dict[str, Any] = Field(default_factory=dict)


class OnRampOrder(BaseModel):
    id: str
    status: str
    fiat_amount: str
    fiat_currency: str
    usdc_amount: Optional[str] = None
    quote_rate: Optional[str] = None
    fee_usd: Optional[str] = None
    raw: Dict[str, Any] = Field(default_factory=dict)


class VelafiError(RuntimeError):
    """Raised for non-2xx responses from the VelaFi API."""

    def __init__(self, status: int, message: str, *, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"VelaFi {status}: {message}")
        self.status = status
        self.message = message
        self.details = details or {}


#VelaFi Client

class VelafiClient:
    """Lightweight async HTTP client for VelaFi API.

    Parameters
    ----------
    api_key:
        Secret key issued by VelaFi. If *None*, the client will look
        for ``VELAFI_API_KEY`` in the environment at runtime (deferred import
        to avoid settings dependency during bootstrap).
    base_url:
        Base URL of VelaFi environment. Defaults to production; set to sandbox
        when running tests (e.g. ``https://sandbox.velafi.com``).
    timeout:
        Request timeout in **seconds**.
    """

    _DEFAULT_TIMEOUT = 30

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.velafi.com", timeout: int | float = _DEFAULT_TIMEOUT):
        if api_key is None:
            # Defer heavy settings import until needed to avoid circulars
            from os import getenv

            api_key = getenv("VELAFI_API_KEY")
        if not api_key:
            raise ValueError("VelaFi API key is required – set VELAFI_API_KEY env var or pass explicitly")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None

        #CHANGE THIS LATER (BASIC CONFIG)
        self.retry_attempts = 3
        self.retry_backoff = 0.5  # seconds, will double per attempt

    #Context Manager 

    async def __aenter__(self):
        await self._ensure_session()
        return self

    async def __aexit__(self, *exc_info):  # noqa: D401 – explicit names
        if self._session and not self._session.closed:
            await self._session.close()

    async def _ensure_session(self):
        """Ensure aiohttp session is available."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)

    async def _request(self, method: str, path: str, *, payload: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make an HTTP request to the VelaFi API."""
        await self._ensure_session()
        
        url = f"{self.base_url}{path}"
        request_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        if headers:
            request_headers.update(headers)
        
        try:
            async with self._session.request(
                method, url, json=payload, headers=request_headers
            ) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    try:
                        error_data = await response.json()
                    except:
                        error_data = {"message": error_text}
                    
                    raise VelafiError(
                        status=response.status,
                        message=error_data.get("message", f"HTTP {response.status}"),
                        details=error_data
                    )
                
                if response.status == 204:  # No content
                    return {}
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            raise VelafiError(0, f"Network error: {e}")

    def _generate_idempotency_key(self, payload: Dict[str, Any]) -> str:
        """Generate an idempotency key from payload."""
        payload_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode()).hexdigest()

    def _parse_order(self, data: Dict[str, Any]) -> OnRampOrder:
        """Parse order response into OnRampOrder model."""
        return OnRampOrder(
            id=data.get("id"),
            status=data.get("status"),
            fiat_amount=data.get("amount") or data.get("fiat_amount"),
            fiat_currency=data.get("currency") or data.get("fiat_currency", "USD"),
            usdc_amount=data.get("usdc_amount"),
            quote_rate=data.get("quote_rate"),
            fee_usd=data.get("fee_usd"),
            raw=data,
        )

    #Public API 

    async def add_payment_method(self, plaid_token: str, *, user_id: str) -> PaymentMethod:
        """Create & return a VelaFi payment method for the given Plaid token.

        Notes
        -----
        • Endpoint: ``POST /v1/payment_methods`` (subject to change).  
        • Uses an idempotency key built from *(user_id, plaid_token)* so that
          repeated submissions within a short window return the same record.
        """

        path = "/v1/payment_methods"
        payload = {
            "plaid_token": plaid_token,
            "customer_reference": user_id,
        }
        headers = {
            "Idempotency-Key": self._generate_idempotency_key(payload),
        }

        resp = await self._request("POST", path, payload=payload, headers=headers)

        return PaymentMethod(
            id=resp.get("id"),
            fiat_rail=resp.get("payment_rail") or resp.get("fiat_rail", "ach"),
            country=resp.get("country", "US"),
            currency=resp.get("currency", "USD"),
            raw=resp,
        )

    async def create_order(self, *, user_id: str, payment_method_id: str, fiat_amount: str) -> OnRampOrder:
        """Create a fiat→crypto on-ramp order.

        Parameters
        ----------
        user_id:
            Liquicity internal user ID (used for metadata / on-behalf-of).
        payment_method_id:
            ID returned from :pymeth:`add_payment_method`.
        fiat_amount:
            Decimal amount (as string) to debit in the currency of the payment
            method (USD for v1).
        """

        path = "/v1/orders/fiat_to_crypto"
        payload = {
            "payment_method_id": payment_method_id,
            "amount": fiat_amount,
            "currency": "USD",
            "metadata": {"user_id": user_id},
        }
        headers = {
            "Idempotency-Key": self._generate_idempotency_key(payload),
        }

        resp = await self._request("POST", path, payload=payload, headers=headers)
        return self._parse_order(resp)

    async def get_order(self, order_id: str) -> OnRampOrder:
        """Retrieve an existing on-ramp order from VelaFi."""

        path = f"/v1/orders/{order_id}"
        resp = await self._request("GET", path)
        return self._parse_order(resp)

    async def get_account(self) -> Dict[str, Any]:
        """Return account details for the authenticated API key (no side-effects).

        Endpoint: ``GET /v1/account`` – documented in VelaFi API reference › Account › Get Account Details.
        Suitable for sandbox key validation.
        """
        path = "/v1/account"
        return await self._request("GET", path)

    async def get_wallets(self, limit: int = 10) -> list[Dict[str, Any]]:
        """Retrieve a list of wallets (experimental – may not be available in all tenants)."""
        path = "/v1/wallets"
        return await self._request("GET", path)  # returns list or {"data": [...]}

    #Ref data/Quotes (read only data)

    async def list_countries(self) -> list[Dict[str, Any]]:
        """Return list of supported countries (docs › Basic Configuration › Get List of Countries)."""
        return await self._request("GET", "/v1/basic/countries")

    async def get_countries(self) -> list[Dict[str, Any]]:
        """Alias for list_countries."""
        return await self.list_countries()

    async def list_fiat_currencies(self) -> list[Dict[str, Any]]:
        return await self._request("GET", "/v1/basic/fiat_currencies")

    async def list_crypto_currencies(self) -> list[Dict[str, Any]]:
        return await self._request("GET", "/v1/basic/crypto_currencies")

    async def list_pairs(self, pair_type: str = "fiat_crypto") -> list[Dict[str, Any]]:
        """Return currency pairs.

        pair_type: one of `fiat_crypto`, `crypto_fiat`, `fiat_fiat`
        """
        return await self._request("GET", f"/v1/basic/pairs?type={pair_type}")

    async def get_quote(self, fiat_amount: float, fiat_currency: str, country: str) -> Dict[str, Any]:
        """Get a quote for fiat to crypto conversion."""
        payload = {
            "fiat_amount": str(fiat_amount),
            "fiat_currency": fiat_currency,
            "country": country
        }
        return await self._request("POST", "/v1/quotes", payload=payload)

    async def get_quote_crypto_to_fiat(
        self,
        user_id: str,
        crypto_symbol: str,
        fiat_symbol: str,
        crypto_amount: str,
    ) -> Dict[str, Any]:
        """Return a quote object converting crypto→fiat (docs › Quote)."""
        payload = {
            "user_id": user_id,
            "from_symbol": crypto_symbol,
            "to_symbol": fiat_symbol,
            "from_amount": crypto_amount,
        }
        return await self._request("POST", "/v1/quote/crypto_to_fiat", payload=payload)

    async def get_quote_fiat_to_fiat(
        self,
        user_id: str,
        from_currency: str,
        to_currency: str,
        fiat_amount: str,
    ) -> Dict[str, Any]:
        payload = {
            "user_id": user_id,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "from_amount": fiat_amount,
        }
        return await self._request("POST", "/v1/quote/fiat_to_fiat", payload=payload)

    #Payment Methods

    async def list_payment_templates(self) -> list[Dict[str, Any]]:
        """Return available bank/rail templates (docs › Payment Method › Get Payment Templates)."""
        return await self._request("GET", "/v1/payment_methods/templates")

    async def get_payment_method(self, payment_method_id: str) -> Dict[str, Any]:
        path = f"/v1/payment_methods/{payment_method_id}"
        return await self._request("GET", path)

    async def delete_payment_method(self, payment_method_id: str) -> None:
        path = f"/v1/payment_methods/{payment_method_id}"
        await self._request("DELETE", path)

    async def set_refund_account(self, payment_method_id: str, account_id: str) -> Dict[str, Any]:
        """Associate a refund account with an existing payment-method."""
        path = f"/v1/payment_methods/{payment_method_id}/refund_account"
        payload = {"refund_account_id": account_id}
        return await self._request("PATCH", path, payload=payload)

    # ------------------------- KYC Methods -------------------------
    
    async def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a VelaFi customer for KYC purposes.
        
        Endpoint: POST /v1/customers
        """
        path = "/v1/customers"
        headers = {
            "Idempotency-Key": self._generate_idempotency_key(customer_data),
        }
        return await self._request("POST", path, payload=customer_data, headers=headers)
    
    async def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Get customer details from VelaFi.
        
        Endpoint: GET /v1/customers/{customer_id}
        """
        path = f"/v1/customers/{customer_id}"
        return await self._request("GET", path)
    
    async def update_customer(self, customer_id: str, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer information in VelaFi.
        
        Endpoint: PUT /v1/customers/{customer_id}
        """
        path = f"/v1/customers/{customer_id}"
        headers = {
            "Idempotency-Key": self._generate_idempotency_key(customer_data),
        }
        return await self._request("PUT", path, payload=customer_data, headers=headers)
    
    async def create_kyc_session(self, customer_id: str, kyc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a KYC session for document verification.
        
        Endpoint: POST /v1/customers/{customer_id}/kyc_sessions
        """
        path = f"/v1/customers/{customer_id}/kyc_sessions"
        headers = {
            "Idempotency-Key": self._generate_idempotency_key(kyc_data),
        }
        return await self._request("POST", path, payload=kyc_data, headers=headers)
    
    async def get_kyc_status(self, customer_id: str) -> Dict[str, Any]:
        """Get KYC verification status for a customer.
        
        Endpoint: GET /v1/customers/{customer_id}/kyc_status
        """
        path = f"/v1/customers/{customer_id}/kyc_status"
        return await self._request("GET", path)
    
    async def upload_document(self, customer_id: str, document_type: str, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Upload a KYC document to VelaFi.
        
        Endpoint: POST /v1/customers/{customer_id}/documents
        """
        path = f"/v1/customers/{customer_id}/documents"
        
        # Prepare multipart form data
        form_data = aiohttp.FormData()
        form_data.add_field('document_type', document_type)
        form_data.add_field('file', file_data, filename=filename)
        
        headers = {
            "Idempotency-Key": self._generate_idempotency_key({"document_type": document_type, "filename": filename}),
        }
        
        return await self._request("POST", path, form_data=form_data, headers=headers)
    
    async def list_kyc_documents(self, customer_id: str) -> list[Dict[str, Any]]:
        """List all KYC documents for a customer.
        
        Endpoint: GET /v1/customers/{customer_id}/documents
        """
        path = f"/v1/customers/{customer_id}/documents"
        return await self._request("GET", path)
    
    async def delete_kyc_document(self, customer_id: str, document_id: str) -> None:
        """Delete a KYC document.

        Endpoint: DELETE /v1/customers/{customer_id}/documents/{document_id}
        """
        path = f"/v1/customers/{customer_id}/documents/{document_id}"
        await self._request("DELETE", path)

    #Signature VErification ( Use a diff method for this later)

    def verify_signature(self, payload: bytes, signature_header: str, secret: str) -> bool:
        """Verify the `x-velafi-signature` HMAC header sent by VelaFi webhooks.

        Header format: ``t=timestamp,v1=hex_digest``.  We recompute the digest
        using the shared webhook secret and constant-time compare.
        """

        try:
            # Split header like "t=1705368000,v1=abc123..."
            parts = dict(kv.split("=", 1) for kv in signature_header.split(","))
            timestamp = parts.get("t")
            their_sig = parts.get("v1")
        except ValueError:
            return False

        if not (timestamp and their_sig):
            return False

        signed = f"{timestamp}.{payload.decode()}".encode()
        expected_sig = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_sig, their_sig)