"""Async client wrapper for the VelaFi REST API.

Only the public method signatures are implemented at this stage. Logic will be
added in subsequent sub-tasks.
"""
from __future__ import annotations

import aiohttp
import asyncio
import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field

_logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic models – request / response stubs (will be fleshed out later)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# VelafiClient
# ---------------------------------------------------------------------------


class VelafiClient:
    """Lightweight async HTTP client for VelaFi API.

    Parameters
    ----------
    api_key:
        Secret key issued by VelaFi dashboard. If *None*, the client will look
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

        # Basic back-off config (can be overridden later)
        self.retry_attempts = 3
        self.retry_backoff = 0.5  # seconds, will double per attempt

    # ---------------------------------------------------------------------
    # Context manager helpers
    # ---------------------------------------------------------------------

    async def __aenter__(self):
        await self._ensure_session()
        return self

    async def __aexit__(self, *exc_info):  # noqa: D401 – explicit names
        if self._session and not self._session.closed:
            await self._session.close()

    # ---------------------------------------------------------------------
    # Public API stubs – implementation in later tasks
    # ---------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Signature verification helper (webhooks)
    # ------------------------------------------------------------------

    def verify_signature(self, payload: bytes, signature_header: str, secret: str) -> bool:
        """Verify `x-velafi-signature` HMAC header.

        Header format: ``t=timestamp,v1=hex_signature``. Timestamp tolerance is
        not checked here – caller should compare to an acceptable window.
        """
        try:
            parts = {k: v for k, v in (kv.split("=", 1) for kv in signature_header.split(","))}
        except ValueError:
            return False

        timestamp = parts.get("t")
        signature = parts.get("v1")
        if not (timestamp and signature):
            return False

        signed_payload = f"{timestamp}.{payload.decode()}".encode()
        expected_sig = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_sig, signature)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout, connect=10)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "Liquicity-VelaFi-Client/1.0",
                },
            )
        return self._session

    async def _request(
        self,
        method: str,
        path: str,
        *,
        payload: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        attempt = 0
        while True:
            attempt += 1
            try:
                session = await self._ensure_session()
                req_headers = headers or {}
                async with session.request(method.upper(), url, json=payload, headers=req_headers) as resp:
                    if resp.status >= 400:
                        text = await resp.text()
                        raise VelafiError(resp.status, text)
                    return await resp.json()
            except Exception as exc:  # noqa: BLE001 – propagate generic
                if attempt > self.retry_attempts:
                    _logger.error("VelaFi request failed after %s attempts: %s", attempt, exc)
                    raise
                backoff = self.retry_backoff * (2 ** (attempt - 1))
                _logger.warning("VelaFi request failed (attempt %s), retrying in %.2fs", attempt, backoff)
                await asyncio.sleep(backoff)

    @staticmethod
    def _generate_idempotency_key(seed: Dict[str, Any]) -> str:
        """Return a SHA-256 digest suitable for VelaFi idempotency header."""
        json_blob = json.dumps(seed, sort_keys=True).encode()
        return hashlib.sha256(json_blob).hexdigest()

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_order(data: Dict[str, Any]) -> OnRampOrder:
        return OnRampOrder(
            id=data.get("id"),
            status=data.get("status"),
            fiat_amount=str(data.get("fiat_amount") or data.get("amount")),
            fiat_currency=data.get("fiat_currency", "USD"),
            usdc_amount=str(data.get("usdc_amount") or data.get("crypto_amount")) if data.get("usdc_amount") or data.get("crypto_amount") else None,
            quote_rate=str(data.get("quote_rate")) if data.get("quote_rate") else None,
            fee_usd=str(data.get("fee_usd")) if data.get("fee_usd") else None,
            raw=data,
        ) 