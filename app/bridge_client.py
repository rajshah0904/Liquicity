import os, uuid, logging, json
import httpx
from typing import Any, Dict

logger = logging.getLogger(__name__)

BRIDGE_BASE_URL = os.getenv("BRIDGE_API_URL", "https://api.bridge.xyz/v0")
BRIDGE_API_KEY = os.getenv("BRIDGE_API_KEY")

class BridgeClient:
    """Lightweight wrapper around Bridge REST API (v0)."""

    def __init__(self) -> None:
        if not BRIDGE_API_KEY:
            logger.warning("BRIDGE_API_KEY not set; client will operate in dry-run mode.")
        self.headers = {
            "Content-Type": "application/json",
            "Api-Key": BRIDGE_API_KEY or "",  # empty in dry-run
        }

    async def create_customer(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST /customers. Returns Bridge response or echo when dry-run."""
        idemp = str(uuid.uuid4())
        self.headers["Idempotency-Key"] = idemp
        url = f"{BRIDGE_BASE_URL}/customers"
        if not BRIDGE_API_KEY:
            logger.info("[DRY-RUN] Would POST to %s: %s", url, json.dumps(payload))
            return {"id": f"dry_{idemp}", "kyc_status": "active", "endorsements": []}
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def _request(self, method: str, path: str, **kwargs):
        """Internal helper for making Bridge API requests respecting dry-run mode."""
        url = f"{BRIDGE_BASE_URL}{path}"
        if not BRIDGE_API_KEY:
            logger.info("[DRY-RUN] %s %s with params=%s json=%s", method.upper(), url, kwargs.get("params"), kwargs.get("json"))
            # Return dummy data structures depending on endpoint path
            if path.startswith("/wallets") and method.lower() == "get":
                if path.count("/") <= 2:  # /wallets
                    return [{"id": "wallet_test", "currency": "usdc", "balance": "100.00"}]
                else:  # /wallets/{id}/history
                    return {"resources": []}
            if path.startswith("/exchange_rates"):
                return {"from": kwargs.get("params", {}).get("from"), "to": kwargs.get("params", {}).get("to"), "rate": 1.0}
            return {}
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.request(method, url, headers=self.headers, **kwargs)
            resp.raise_for_status()
            return resp.json()

    async def list_wallets(self, customer_id: str | None = None):
        """GET /wallets. Optionally filter by on_behalf_of customer_id."""
        params = {"on_behalf_of": customer_id} if customer_id else None
        return await self._request("get", "/wallets", params=params)

    async def wallet_history(self, wallet_id: str, since: str | None = None):
        """GET /wallets/{wallet_id}/history. Accept optional since timestamp."""
        params = {"since": since} if since else None
        return await self._request("get", f"/wallets/{wallet_id}/history", params=params)

    async def get_exchange_rate(self, from_curr: str, to_curr: str):
        """GET /exchange_rates?from=xyz&to=abc"""
        params = {"from": from_curr, "to": to_curr}
        return await self._request("get", "/exchange_rates", params=params) 