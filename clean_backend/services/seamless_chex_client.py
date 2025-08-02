"""Seamless Chex API client (minimal stub)

This client provides just enough functionality for ACH debits initiated after a user
links a bank account via Plaid.  In production you must replace the placeholder logic
with real HTTPS calls and handle signatures, webhooks, idempotency, etc.
"""
from __future__ import annotations

import os
import uuid
from decimal import Decimal
from typing import Dict, Any, Optional

import httpx


class SeamlessChexError(RuntimeError):
    """Raised when the Seamless Chex API returns an error."""


class SeamlessChexClient:
    BASE_URL = os.getenv("SEAMLESSCHEX_BASE_URL", "https://api.seamlesschex.com/v1")

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SEAMLESSCHEX_API_KEY")
        if not self.api_key:
            raise RuntimeError("Missing SEAMLESSCHEX_API_KEY environment variable")
        self.session = httpx.Client(base_url=self.BASE_URL, headers={"Authorization": f"Bearer {self.api_key}"})

    def _post(self, path: str, json: Dict[str, Any]) -> Dict[str, Any]:
        resp = self.session.post(path, json=json, timeout=30)
        if resp.status_code >= 400:
            raise SeamlessChexError(f"HTTP {resp.status_code}: {resp.text}")
        return resp.json()

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def initiate_debit(
        self,
        processor_token: str,
        amount: Decimal,
        currency: str = "USD",
        description: Optional[str] = None,
        destination_account_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Submit an ACH debit request using a Plaid processor_token.

        NOTE: This is a *placeholder* implementation – you must replace the
        endpoint and payload with the actual Seamless Chex spec.
        """
        if idempotency_key is None:
            idempotency_key = str(uuid.uuid4())

        payload = {
            "processor_token": processor_token,
            "amount": str(amount),
            "currency": currency.lower(),
            "description": description or "Liquicity deposit",
            "destination_account_id": destination_account_id,
            "idempotency_key": idempotency_key,
        }
        # TODO: update path to the real Seamless Chex endpoint
        return self._post("/debits", payload) 