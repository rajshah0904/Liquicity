from __future__ import annotations

from typing import Any, Dict
import os
import requests

# Map Plaid environments → base URLs
_PLAID_BASE_URLS: Dict[str, str] = {
    "sandbox": "https://sandbox.plaid.com",
    "development": "https://development.plaid.com",
    "production": "https://production.plaid.com",
}

class PlaidClient:
    """Minimal Plaid REST client covering public_token exchange, Auth, Balance and Identity."""

    def __init__(self) -> None:
        self.client_id: str | None = os.getenv("PLAID_CLIENT_ID")
        self.secret: str | None = os.getenv("PLAID_SECRET")
        if not self.client_id or not self.secret:
            raise RuntimeError("PLAID_CLIENT_ID and PLAID_SECRET env vars must be set")

        env = os.getenv("PLAID_ENV", "sandbox").lower()
        self.base_url: str = _PLAID_BASE_URLS.get(env, _PLAID_BASE_URLS["sandbox"])

    # ---------------- Internal helpers ---------------- #
    def _post(self, path: str, json: Dict[str, Any]) -> Dict[str, Any]:
        payload = {"client_id": self.client_id, "secret": self.secret, **json}
        resp = requests.post(f"{self.base_url}{path}", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # ---------------- Public API wrappers ------------- #
    def exchange_public_token(self, public_token: str) -> Dict[str, Any]:
        """Exchange a temporary *public_token* for a long-lived *access_token*."""
        return self._post("/item/public_token/exchange", {"public_token": public_token})

    def get_auth(self, access_token: str) -> Dict[str, Any]:
        return self._post("/auth/get", {"access_token": access_token})

    def get_balance(self, access_token: str) -> Dict[str, Any]:
        return self._post("/accounts/balance/get", {"access_token": access_token})

    def get_identity(self, access_token: str) -> Dict[str, Any]:
        return self._post("/identity/get", {"access_token": access_token})

    # ---------------- Processor integrations ------------- #
    def create_processor_token(
        self,
        access_token: str,
        account_id: str,
        processor: str = "finix",
    ) -> Dict[str, Any]:
        """Create a Plaid *processor_token* to be passed to a payment processor (e.g. Finix).

        Docs:
          – Generic  : POST /processor/token/create
          – Finix    : POST /processor/finix/bank_account_token/create

        We default to the Finix-specific endpoint because that avoids needing an
        additional parameter in the request body.  For other processors, callers
        can pass ``processor="stripe"`` or any supported value and the generic
        endpoint will be used instead.
        """

        processor = processor.lower()

        if processor == "finix":
            path = "/processor/finix/bank_account_token/create"
            body = {
                "access_token": access_token,
                "account_id": account_id,
            }
        else:
            # Fallback to the generic endpoint – requires explicit processor value
            path = "/processor/token/create"
            body = {
                "access_token": access_token,
                "account_id": account_id,
                "processor": processor,
            }

        return self._post(path, body) 