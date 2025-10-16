from __future__ import annotations

from typing import Any, Dict, Optional
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
        self.client_id: Optional[str] = os.getenv("PLAID_CLIENT_ID")
        self.secret: Optional[str] = os.getenv("PLAID_SECRET")
        if not self.client_id or not self.secret:
            raise RuntimeError("PLAID_CLIENT_ID and PLAID_SECRET env vars must be set")

        env = os.getenv("PLAID_ENV", "sandbox").lower()
        self.base_url: str = _PLAID_BASE_URLS.get(env, _PLAID_BASE_URLS["sandbox"])
        print(f"🔧 PlaidClient initialized with environment: {env}")
        print(f"🌐 Using Plaid base URL: {self.base_url}")

    # ---------------- Internal helpers ---------------- #
    def _post(self, path: str, json: Dict[str, Any]) -> Dict[str, Any]:
        payload = {"client_id": self.client_id, "secret": self.secret, **json}
        resp = requests.post(f"{self.base_url}{path}", json=payload, timeout=30)
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            # Surface Plaid's error body to callers for easier debugging
            detail = resp.text if resp is not None else str(e)
            raise requests.HTTPError(f"{e}\nPlaid body: {detail}") from e
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

    def create_link_token(self, user_id: str, webhook_url: Optional[str] = None, redirect_uri: Optional[str] = None) -> Dict[str, Any]:
        """Create a link_token for initializing Plaid Link."""
        payload = {
            "products": ["auth", "identity"],
            "client_name": "Liquicity",
            "country_codes": ["US"],
            "language": "en", 
            "user": {
                "client_user_id": user_id
            }
        }
        
        if webhook_url:
            payload["webhook"] = webhook_url
        if redirect_uri:
            payload["redirect_uri"] = redirect_uri
        
        return self._post("/link/token/create", payload)

    # ---------------- EU Payments (Payment Initiation) ------------- #
    def create_eu_link_token(
        self,
        user_id: str,
        *,
        country_codes: Optional[list[str]] = None,
        payment_id: Optional[str] = None,
        institution_id: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        language: str = "en",
    ) -> Dict[str, Any]:
        """Create a Plaid Link token for EU Payment Initiation.

        If payment_id is provided, the token will be scoped to authorizing that payment.
        Docs: https://plaid.com/docs/payment-initiation/#overview
        """
        if country_codes is None:
            # Prefer settings-driven country list so we can match enabled geographies
            env_codes = None
            try:
                # Lazy import to avoid any circular import at module import time
                from ..config.settings import settings as _settings  # type: ignore
                env_codes = getattr(_settings, "plaid_country_codes_eu", None)
            except Exception:
                env_codes = None

            if env_codes and isinstance(env_codes, list) and len(env_codes) > 0:
                country_codes = env_codes
            else:
                # Minimal default to avoid INVALID_FIELD when keys have narrow access
                country_codes = ["GB"]

        payload: Dict[str, Any] = {
            "products": ["payment_initiation"],
            "client_name": "Liquicity",
            "country_codes": country_codes,
            "language": language,
            "user": {"client_user_id": user_id},
        }

        # Attach payment to Link if provided
        if payment_id:
            payload["payment_initiation"] = {"payment_id": payment_id}

        # Optionally preselect institution
        if institution_id:
            payload["institution_id"] = institution_id

        if redirect_uri:
            payload["redirect_uri"] = redirect_uri

        return self._post("/link/token/create", payload)

    # ---------------- EU Auth (retrieve IBAN/BIC) ------------------ #
    def create_eu_auth_link_token(
        self,
        user_id: str,
        *,
        country_codes: Optional[list[str]] = None,
        redirect_uri: Optional[str] = None,
        language: str = "en",
    ) -> Dict[str, Any]:
        """Create a Plaid Link token for EU/UK Auth in order to retrieve bank identifiers.

        Products: ["auth"]. Country codes must be enabled for your keys.
        """
        if country_codes is None:
            env_codes = None
            try:
                from ..config.settings import settings as _settings  # type: ignore
                env_codes = getattr(_settings, "plaid_country_codes_eu", None)
            except Exception:
                env_codes = None
            if env_codes and isinstance(env_codes, list) and len(env_codes) > 0:
                country_codes = env_codes
            else:
                country_codes = ["GB"]

        payload: Dict[str, Any] = {
            "products": ["auth", "identity"],
            "client_name": "Liquicity",
            "country_codes": country_codes,
            "language": language,
            "user": {"client_user_id": user_id},
        }
        if redirect_uri:
            payload["redirect_uri"] = redirect_uri
        return self._post("/link/token/create", payload)

    def pi_recipient_create(
        self,
        *,
        name: str,
        iban: str,
        address: Optional[Dict[str, Any]] = None,
        bacs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create Payment Initiation recipient.

        Minimal for SEPA: name + IBAN. Address is recommended by some banks.
        """
        body: Dict[str, Any] = {
            "name": name,
            "iban": iban,
        }
        if address:
            body["address"] = address
        if bacs:
            body["bacs"] = bacs
        return self._post("/payment_initiation/recipient/create", body)

    def pi_recipient_get(self, recipient_id: str) -> Dict[str, Any]:
        return self._post("/payment_initiation/recipient/get", {"recipient_id": recipient_id})

    def pi_payment_create(
        self,
        *,
        recipient_id: str,
        reference: str,
        amount_value: str,
        amount_currency: str = "EUR",
        schedule: Optional[Dict[str, Any]] = None,
        request_idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a Payment Initiation payment.

        amount_value should be decimal string with 2 dp (e.g. "10.00").
        """
        body: Dict[str, Any] = {
            "recipient_id": recipient_id,
            "reference": reference,
            "amount": {"currency": amount_currency, "value": amount_value},
        }
        if schedule:
            body["schedule"] = schedule
        if request_idempotency_key:
            body["idempotency_key"] = request_idempotency_key
        return self._post("/payment_initiation/payment/create", body)

    def pi_payment_get(self, payment_id: str) -> Dict[str, Any]:
        return self._post("/payment_initiation/payment/get", {"payment_id": payment_id})

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