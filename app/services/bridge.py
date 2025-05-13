import os, uuid, httpx, logging
from typing import Any, Dict, Optional
from decimal import Decimal
from sqlalchemy import text
from app.database import engine

BASE_URL = "https://api.bridge.xyz/v0"
API_KEY  = os.getenv("BRIDGE_API_KEY", "demo")  # ← replace in production
DEMO_MODE = API_KEY == "demo" or os.getenv("BRIDGE_DEMO_MODE")

_log = logging.getLogger(__name__)

def _headers(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    h = {
        "Api-Key": API_KEY,
        "Content-Type": "application/json",
    }
    if extra:
        h.update(extra)
    return h

class _DemoBridgeClient:
    """In-process stub that mimics Bridge when we run in demo mode (no real API key)."""
    def __init__(self):
        pass

    # ------------------ helpers ------------------
    def _ensure_wallet(self, customer_id: str) -> Dict[str, Any]:
        """Create a demo wallet row if missing and return it."""
        with engine.begin() as conn:
            row = conn.execute(text("""
                SELECT w.wallet_id, w.balance, w.currency
                FROM demo_wallets w
                JOIN users u ON u.id = w.user_id
                WHERE u.bridge_customer_id = :cid
            """), {"cid": customer_id}).first()
            if row:
                return {"id": row[0], "balance": str(row[1]), "currency": row[2]}
            # Need to create new wallet row
            user = conn.execute(text("SELECT id, country FROM users WHERE bridge_customer_id = :cid"), {"cid": customer_id}).first()
            if not user:
                # Should not happen – caller must have user row
                raise ValueError("Unknown customer id in demo mode")
            user_id, country_code = user
            # Determine currency from country (US→USD, EU list→EUR, MX→MXN)
            currency = "usd"
            if country_code:
                cc = country_code.upper()
                if cc == "MX":
                    currency = "mxn"
                elif cc in [
                    "AT","BE","BG","CH","CY","CZ","DE","DK","EE","ES","FI","FR","GB","GR","HR","HU","IE","IS","IT","LI","LT","LU","LV","MT","NL","NO","PL","PT","RO","SE","SI","SK"
                ]:
                    currency = "eur"
            wallet_id = f"demo_wallet_{uuid.uuid4().hex[:8]}"
            conn.execute(text("""
                INSERT INTO demo_wallets (user_id, wallet_id, balance, currency) VALUES (:uid, :wid, 0, :cur)
            """), {"uid": user_id, "wid": wallet_id, "cur": currency})
            return {"id": wallet_id, "balance": "0", "currency": currency}

    # ------------- API method stubs -------------
    async def create_customer(self, payload: Dict[str, Any]):
        cid = f"demo_cust_{uuid.uuid4().hex[:8]}"
        # payload lacks db session; we update users via engine
        email = payload.get("email")
        first = payload.get("first_name")
        last = payload.get("last_name")
        with engine.begin() as conn:
            # try update user by email if exists
            if email:
                conn.execute(text("UPDATE users SET bridge_customer_id = :cid WHERE email = :em"), {"cid": cid, "em": email})
        return {"id": cid, "kyc_status": "approved"}

    async def create_external_account(self, customer_id: str, payload: Dict[str, Any]):
        return {"id": f"demo_ext_{uuid.uuid4().hex[:6]}", **payload}

    async def create_card(self, customer_id: str, payload: Dict[str, Any]):
        return {"id": f"demo_card_{uuid.uuid4().hex[:6]}", "last4": "4242", "state": "active", **payload}

    async def list_wallets(self, customer_id: Optional[str] = None):
        if not customer_id:
            # Return treasury wallet with large balance
            return [{"id": "treasury_demo", "currency": "usd", "balance": "1000000"}]
        w = self._ensure_wallet(customer_id)
        return [w]

    async def get_wallets(self, customer_id: Optional[str] = None):
        return await self.list_wallets(customer_id)

    async def wallet_history(self, wallet_id: str, since: Optional[str] = None):
        # Not implemented – return empty list for demo purposes
        return []

    async def create_transfer(self, payload: Dict[str, Any]):
        """Very naive balance-transfer simulation."""
        amount = Decimal(str(payload.get("amount")))
        dev_fee = Decimal(str(payload.get("developer_fee", "0")))
        src = payload.get("source", {})
        dst = payload.get("destination", {})
        bridge_id = f"demo_tx_{uuid.uuid4().hex[:10]}"

        # Determine conversion if needed
        src_curr = src.get("currency")
        dst_curr = dst.get("currency")
        rate = Decimal("1")
        if src_curr and dst_curr and src_curr.lower() != dst_curr.lower():
            rate_resp = await self.get_exchange_rate(src_curr.lower(), dst_curr.lower())
            rate = Decimal(str(rate_resp.get("rate", "1")))

        credit_amount = (amount * rate).quantize(Decimal("0.01"))

        with engine.begin() as conn:
            # debit source wallet if polygon
            if src.get("payment_rail") == "polygon":
                wid = src.get("wallet_id")
                # developer_fee deducted on sender side
                conn.execute(text("UPDATE demo_wallets SET balance = balance - :amt - :fee WHERE wallet_id = :wid"), {"amt": amount, "fee": dev_fee, "wid": wid})
            # credit destination wallet if polygon
            if dst.get("payment_rail") == "polygon":
                wid = dst.get("wallet_id")
                # guard row creation
                conn.execute(text("INSERT INTO demo_wallets (user_id, wallet_id, balance, currency) SELECT u.id, :wid, 0, :cur FROM users u WHERE u.bridge_customer_id = :cid ON CONFLICT (wallet_id) DO NOTHING"), {
                    "wid": wid,
                    "cid": payload.get("on_behalf_of"),
                    "cur": dst_curr or "usd",
                })
                conn.execute(text("UPDATE demo_wallets SET balance = balance + :amt WHERE wallet_id = :wid"), {"amt": credit_amount, "wid": wid})
        return {"id": bridge_id, "state": "succeeded", "debited": str(amount), "credited": str(credit_amount), "fee": str(dev_fee)}

    async def plaid_link_request(self, customer_id: str):
        return {"link_token": f"demo_link_{customer_id}"}

    async def plaid_exchange_token(self, request_id: str):
        return {"access_token": f"demo_access_{request_id}"}

    async def get_customer(self, customer_id: str):
        return {"id": customer_id, "kyc_status": "approved"}

    async def get_exchange_rate(self, from_curr: str, to_curr: str):
        from_curr = from_curr.lower()
        to_curr = to_curr.lower()
        if (from_curr, to_curr) == ("usd", "eur"):
            return {"rate": "0.92"}
        if (from_curr, to_curr) == ("eur", "usd"):
            return {"rate": "1.087"}
        # identity fallback
        return {"rate": "1"}

    async def close(self):
        pass

class BridgeClient:
    """Thin async wrapper around Bridge XYZ v0 HTTP API or local stub when in demo mode."""
    def __init__(self, session: Optional[httpx.AsyncClient] = None) -> None:
        if DEMO_MODE:
            self._demo = _DemoBridgeClient()
            self._is_demo = True
        else:
            self._client = session or httpx.AsyncClient(timeout=20.0, http2=True)
            self._is_demo = False

    # -----------------------------------------------------
    # Internal helpers (real mode)
    # -----------------------------------------------------
    async def _post(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        if self._is_demo:
            raise RuntimeError("_post should not be called in demo mode")
        idem = str(uuid.uuid4())
        url  = f"{BASE_URL}{path}"
        _log.debug("POST %s", url)
        r = await self._client.post(url, json=body, headers=_headers({"Idempotency-Key": idem}))
        r.raise_for_status()
        return r.json()

    async def _put(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        if self._is_demo:
            raise RuntimeError("_put should not be called in demo mode")
        url = f"{BASE_URL}{path}"
        r   = await self._client.put(url, json=body, headers=_headers())
        r.raise_for_status()
        return r.json()

    async def _get(self, path: str, params: Optional[dict] = None) -> Dict[str, Any]:
        if self._is_demo:
            raise RuntimeError("_get should not be called in demo mode")
        url = f"{BASE_URL}{path}"
        r = await self._client.get(url, headers=_headers(), params=params)
        r.raise_for_status()
        return r.json()

    # -----------------------------------------------------
    # Delegate public API
    # -----------------------------------------------------
    async def create_customer(self, payload: Dict[str, Any]):
        if self._is_demo:
            return await self._demo.create_customer(payload)
        return await self._post("/customers", payload)

    async def create_external_account(self, customer_id: str, payload: Dict[str, Any]):
        if self._is_demo:
            return await self._demo.create_external_account(customer_id, payload)
        return await self._post(f"/customers/{customer_id}/external_accounts", payload)

    async def plaid_link_request(self, customer_id: str):
        if self._is_demo:
            return await self._demo.plaid_link_request(customer_id)
        return await self._post(f"/customers/{customer_id}/plaid_link_requests", {})

    async def plaid_exchange_token(self, request_id: str):
        if self._is_demo:
            return await self._demo.plaid_exchange_token(request_id)
        return await self._post(f"/plaid_exchange_public_token/{request_id}", {})

    async def create_card(self, customer_id: str, payload: Dict[str, Any]):
        if self._is_demo:
            return await self._demo.create_card(customer_id, payload)
        return await self._post(f"/customers/{customer_id}/card_accounts", payload)

    async def list_wallets(self, customer_id: Optional[str] = None):
        if self._is_demo:
            return await self._demo.list_wallets(customer_id)
        params = {"on_behalf_of": customer_id} if customer_id else None
        return await self._get("/wallets", params=params)

    async def get_wallets(self, customer_id: Optional[str] = None):
        return await self.list_wallets(customer_id)

    async def wallet_history(self, wallet_id: str, since: Optional[str] = None):
        if self._is_demo:
            return await self._demo.wallet_history(wallet_id, since)
        params = {"since": since} if since else None
        return await self._get(f"/wallets/{wallet_id}/history", params=params)

    async def get_exchange_rate(self, from_curr: str, to_curr: str):
        if self._is_demo:
            return await self._demo.get_exchange_rate(from_curr, to_curr)
        params = {"from": from_curr, "to": to_curr}
        return await self._get("/exchange_rates", params=params)

    async def create_transfer(self, payload: Dict[str, Any]):
        if self._is_demo:
            return await self._demo.create_transfer(payload)
        return await self._post("/transfers", payload)

    async def get_customer(self, customer_id: str):
        if self._is_demo:
            return await self._demo.get_customer(customer_id)
        return await self._get(f"/customers/{customer_id}")

    async def close(self):
        if not self._is_demo:
            await self._client.aclose() 