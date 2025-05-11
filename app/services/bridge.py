import os, uuid, httpx, logging
from typing import Any, Dict, Optional

BASE_URL = "https://api.bridge.xyz/v0"
API_KEY  = os.getenv("BRIDGE_API_KEY", "demo")  # ← replace in production

_log = logging.getLogger(__name__)

def _headers(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    h = {
        "Api-Key": API_KEY,
        "Content-Type": "application/json",
    }
    if extra:
        h.update(extra)
    return h

class BridgeClient:
    """Thin async wrapper around Bridge XYZ v0 HTTP API."""

    def __init__(self, session: Optional[httpx.AsyncClient] = None) -> None:
        self._client = session or httpx.AsyncClient(timeout=20.0, http2=True)

    # -----------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------
    async def _post(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        idem = str(uuid.uuid4())
        url  = f"{BASE_URL}{path}"
        _log.debug("POST %s", url)
        r = await self._client.post(url, json=body, headers=_headers({"Idempotency-Key": idem}))
        r.raise_for_status()
        return r.json()

    async def _put(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{BASE_URL}{path}"
        r   = await self._client.put(url, json=body, headers=_headers())
        r.raise_for_status()
        return r.json()

    async def _get(self, path: str, params: Optional[dict] = None) -> Dict[str, Any]:
        url = f"{BASE_URL}{path}"
        r = await self._client.get(url, headers=_headers(), params=params)
        r.raise_for_status()
        return r.json()

    # -----------------------------------------------------
    # Customers
    # -----------------------------------------------------
    async def create_customer(self, payload: Dict[str, Any]):
        return await self._post("/customers", payload)

    # -----------------------------------------------------
    # External accounts
    # -----------------------------------------------------
    async def create_external_account(self, customer_id: str, payload: Dict[str, Any]):
        return await self._post(f"/customers/{customer_id}/external_accounts", payload)

    # -----------------------------------------------------
    # Plaid helpers
    # -----------------------------------------------------
    async def plaid_link_request(self, customer_id: str):
        return await self._post(f"/customers/{customer_id}/plaid_link_requests", {})

    async def plaid_exchange_token(self, request_id: str):
        return await self._post(f"/plaid_exchange_public_token/{request_id}", {})

    # -----------------------------------------------------
    # Cards
    # -----------------------------------------------------
    async def create_card(self, customer_id: str, payload: Dict[str, Any]):
        return await self._post(f"/customers/{customer_id}/card_accounts", payload)

    # -----------------------------------------------------
    # Wallets
    # -----------------------------------------------------
    async def list_wallets(self, customer_id: Optional[str] = None):
        params = {"on_behalf_of": customer_id} if customer_id else None
        return await self._get("/wallets", params=params)

    async def wallet_history(self, wallet_id: str, since: Optional[str] = None):
        """Return transaction history for a given wallet ID. Optional `since` ISO timestamp."""
        params = {"since": since} if since else None
        return await self._get(f"/wallets/{wallet_id}/history", params=params)

    # -----------------------------------------------------
    # FX & Rates
    # -----------------------------------------------------
    async def get_exchange_rate(self, from_curr: str, to_curr: str):
        """Retrieve latest exchange rate between two currency codes."""
        params = {"from": from_curr, "to": to_curr}
        return await self._get("/exchange_rates", params=params)

    # -----------------------------------------------------
    # Transfers
    # -----------------------------------------------------
    async def create_transfer(self, payload: Dict[str, Any]):
        return await self._post("/transfers", payload)

    # -----------------------------------------------------
    # Customers helpers
    # -----------------------------------------------------
    async def get_customer(self, customer_id: str):
        return await self._get(f"/customers/{customer_id}")

    # -----------------------------------------------------
    async def close(self):
        await self._client.aclose() 