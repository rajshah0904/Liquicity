import os, uuid, requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()  # load variables from .env if present

BASE_URL = os.getenv("BRIDGE_API_URL", "https://api.bridge.xyz/v0")
API_KEY = os.getenv("BRIDGE_API_KEY")

if not API_KEY:
    raise RuntimeError("BRIDGE_API_KEY environment variable must be set (either in the environment or .env file)")


def _headers(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    h = {
        "Api-Key": API_KEY,
        "Content-Type": "application/json",
        "accept": "application/json",
    }
    if extra:
        h.update(extra)
    return h


class BridgeClient:
    """Minimal subset of Bridge API used during onboarding."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"accept": "application/json"})

    # ------------------------- Helper -------------------------
    def _post(self, path: str, json: Dict[str, Any]):
        idem = str(uuid.uuid4())
        resp = self.session.post(
            f"{BASE_URL}{path}",
            json=json,
            headers=_headers({"Idempotency-Key": idem}),
            timeout=30,
        )
        # Bridge returns 400 with {"code":"duplicate_record","existing_kyc_link":{...}} when a link already exists.
        if resp.status_code == 400 and "duplicate_record" in resp.text:
            data = resp.json()
            if "existing_kyc_link" in data:
                return data["existing_kyc_link"]

        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            # Include response text for easier debugging
            raise requests.HTTPError(f"{e}\nResponse body: {resp.text}") from e

        return resp.json()

    # ------------------ Public minimal methods ---------------
    def request_tos_links(self, redirect_uri: str = None) -> Dict[str, Any]:
        """Call POST /customers/tos_links"""
        payload = {}
        if redirect_uri:
            payload["redirect_uri"] = redirect_uri
        return self._post("/customers/tos_links", payload)

    def create_customer(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create Bridge customer (POST /customers). Payload must include signed_agreement_id"""
        return self._post("/customers", payload) 

    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Fetch a Bridge customer by id (GET /customers/{id})."""
        resp = self.session.get(f"{BASE_URL}/customers/{customer_id}", headers=_headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def create_kyc_link(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a hosted KYC link (POST /kyc_links) and return its JSON response."""
        return self._post("/kyc_links", payload)

    # ---------------- Wallet helpers -----------------
    def create_wallet(self, customer_id: str, chain: str = "solana") -> Dict[str, Any]:
        """Create a Bridge wallet for the given customer.

        This calls POST /customers/{customer_id}/wallets with a JSON body of
        {"chain": chain}. By default we create Solana wallets.
        """
        return self._post(f"/customers/{customer_id}/wallets", {"chain": chain})

    def get_wallet(self, customer_id: str, wallet_id: str):
        resp = self.session.get(f"{BASE_URL}/customers/{customer_id}/wallets/{wallet_id}", headers=_headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def list_customer_wallets(self, customer_id: str):
        """List wallets for a given Bridge customer (GET /customers/{customer_id}/wallets)."""
        resp = self.session.get(f"{BASE_URL}/customers/{customer_id}/wallets", headers=_headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_all_wallets(self):
        """Get all wallets from Bridge API"""
        resp = self.session.get(f"{BASE_URL}/wallets", headers=_headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_wallet_balances(self, customer_id: str, wallet_id: str):
        """Get detailed balance information for a specific wallet"""
        try:
            return self.get_wallet(customer_id, wallet_id)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                # If individual wallet endpoint not available, return basic info
                return {
                    "id": wallet_id,
                    "balances": []
                }
            raise

    def get_wallet_history(self, wallet_id: str, params: Optional[dict] = None):
        resp = self.session.get(f"{BASE_URL}/wallets/{wallet_id}/history", headers=_headers(), params=params or {}, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # ------------------- Live status helpers -----------------
    def get_kyc_link(self, link_id: str) -> Dict[str, Any]:
        """Retrieve the latest status of an existing KYC link (GET /kyc_links/{id})."""
        resp = self.session.get(f"{BASE_URL}/kyc_links/{link_id}", headers=_headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()

    # ------------------- Card accounts -----------------
    def create_card_account(
        self,
        customer_id: str,
        *,
        wallet_address: str,
        chain: str = "solana",
        currency: str = "usdc",
        client_reference_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Provision a new card account for the given customer.

        Bridge endpoint: POST /customers/{customer_id}/card_accounts

        Args:
            customer_id: Bridge customer ID that will own the card account.
            wallet_address: Public crypto address that will fund the card (should NOT be the Bridge wallet id).
            chain: Blockchain network (defaults to "solana").
            currency: Crypto currency symbol for the card funding (defaults to "usdc").
            client_reference_id: Optional caller-supplied idempotency string.
        """

        payload: Dict[str, Any] = {
            "currency": currency,
            "chain": chain,
            "crypto_account": {
                "type": "standard",
                "address": wallet_address,
            },
        }

        if client_reference_id:
            payload["client_reference_id"] = client_reference_id

        return self._post(f"/customers/{customer_id}/card_accounts", payload)

    # ---------------- Plaid helpers ----------------
    def get_plaid_link_token(self, customer_id: str):
        """Generate a Plaid Link token for the specified Bridge customer via Bridge API."""
        import uuid
        idem = str(uuid.uuid4())
        resp = self.session.post(
            f"{BASE_URL}/customers/{customer_id}/plaid_link_requests",
            headers=_headers({"Idempotency-Key": idem}),
            json={},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def exchange_plaid_token(self, link_token: str, public_token: str):
        """Exchange a Plaid public_token via Bridge (this endpoint MUST NOT include Idempotency-Key)."""
        payload = {"public_token": public_token}
        url = f"{BASE_URL}/plaid_exchange_public_token/{link_token}"
        resp = self.session.post(url, json=payload, headers=_headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def wait_for_plaid_accounts(self, customer_id: str, initial_count: int = 0, max_attempts: int = 12, delay: int = 5):
        """Wait for Plaid-linked external accounts to be created asynchronously by Bridge.
        
        After a successful Plaid token exchange, Bridge creates external accounts asynchronously.
        This method polls the external accounts endpoint until new accounts appear.
        
        Args:
            customer_id: Bridge customer ID
            initial_count: Number of external accounts before Plaid linking
            max_attempts: Maximum number of polling attempts (default: 12 = 1 minute)
            delay: Delay between attempts in seconds (default: 5)
            
        Returns:
            List of newly created external accounts, or empty list if timeout
        """
        import time
        
        for attempt in range(max_attempts):
            try:
                current_accounts = self.list_external_accounts(customer_id)
                current_count = len(current_accounts.get("data", []))
                
                if current_count > initial_count:
                    # New accounts detected
                    new_accounts = current_accounts.get("data", [])[initial_count:]
                    return new_accounts
                    
                if attempt < max_attempts - 1:  # Don't sleep on last attempt
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"Error polling for Plaid accounts (attempt {attempt + 1}): {e}")
                if attempt < max_attempts - 1:
                    time.sleep(delay)
        
        # Timeout reached
        return []

    # ---------------- External Accounts ----------------
    def list_external_accounts(self, customer_id: str):
        """Return all external accounts for the given customer."""
        resp = self.session.get(f"{BASE_URL}/customers/{customer_id}/external_accounts", headers=_headers(), timeout=30)
        resp.raise_for_status()
        return resp.json() 

    def create_external_account(self, customer_id: str, payload: Dict[str, Any]):
        """Create a new external account for the specified customer (POST /customers/{customer_id}/external_accounts)."""
        return self._post(f"/customers/{customer_id}/external_accounts", payload)

    def get_external_account(self, external_account_id: str, customer_id: Optional[str] = None):
        """Retrieve a single external account.

        Bridge API supports two flavours:
        1. GET /customers/{customer_id}/external_accounts/{id}  ← reliable
        2. GET /external_accounts/{id}                          ← returns 404 for customer-scoped resources

        We attempt the customer-scoped path first when `customer_id` is given, and fall back to the global one.
        """
        paths = []
        if customer_id:
            paths.append(f"/customers/{customer_id}/external_accounts/{external_account_id}")
        paths.append(f"/external_accounts/{external_account_id}")

        last_err = None
        for p in paths:
            try:
                resp = self.session.get(f"{BASE_URL}{p}", headers=_headers(), timeout=30)
                resp.raise_for_status()
                return resp.json()
            except requests.HTTPError as e:
                last_err = e
                # Only try fallback on 404; any other error we propagate immediately
                if e.response is None or e.response.status_code != 404:
                    raise

        # If all attempts failed, raise the last 404 error
        assert last_err is not None
        raise last_err

    # ---------------- Delete External Account ----------------
    def delete_external_account(self, customer_id: str, external_account_id: str):
        """Delete an external account under a customer.

        Wrapper around DELETE /customers/{customer_id}/external_accounts/{id}
        Returns True on success.
        """
        resp = self.session.delete(
            f"{BASE_URL}/customers/{customer_id}/external_accounts/{external_account_id}",
            headers=_headers(), 
            timeout=30,
        )
        if resp.status_code == 404:
            raise requests.HTTPError("External account not found", response=resp)
        resp.raise_for_status()
        return resp.json() if resp.text else {"deleted": True}

    # ---------------- Virtual Accounts ----------------

    def create_virtual_account(self, customer_id: str, payload: Optional[Dict[str, Any]] = None):
        """Create a new virtual account for the customer.

        By default creates a USD virtual account that converts to USDC on Solana.
        """
        if payload is None:
            payload = {
                "source": {"currency": "usd"},
                "destination": {
                    "payment_rail": "solana",
                    "currency": "usdc",
                    "address": "AUTO",  # Backend should replace with wallet address
                },
            }
        return self._post(f"/customers/{customer_id}/virtual_accounts", payload)

    def list_virtual_accounts(self, customer_id: str):
        """Return all virtual accounts for a customer."""
        resp = self.session.get(f"{BASE_URL}/customers/{customer_id}/virtual_accounts", headers=_headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_or_create_usd_virtual_account(self, customer_id: str, wallet_address: Optional[str] = None):
        """Idempotent helper: return existing VA id or create a USD→USDC(Solana) account once."""
        # 1. Check existing
        try:
            existing = self.list_virtual_accounts(customer_id)
            data = existing.get("data", []) if isinstance(existing, dict) else existing.get("data", [])
            if data:
                return data[0]  # return first existing
        except Exception:
            pass  # listing failed shouldn't block creation

        # 2. Create
        payload = {
            "source": {"currency": "usd"},
            "destination": {
                "payment_rail": "solana",
                "currency": "usdc",
            },
        }
        if wallet_address:
            payload["destination"]["address"] = wallet_address
        return self.create_virtual_account(customer_id, payload) 

    # ------------------- Transfers -----------------
    def create_transfer_sync(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Bridge transfer and return the resulting JSON.

        This is a thin wrapper around POST /transfers so we can reuse
        the same client throughout the backend.
        """
        return self._post("/transfers", payload) 

    def get_transfer(self, transfer_id: str) -> Dict[str, Any]:
        """Fetch a transfer by id (GET /transfers/{id})."""
        resp = self.session.get(f"{BASE_URL}/transfers/{transfer_id}", headers=_headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def delete_transfer(self, transfer_id: str):
        """Delete (cancel) a transfer that is still in awaiting_funds state.

        Wrapper around DELETE /transfers/{id}. Returns JSON response.
        """
        idem = str(uuid.uuid4())
        resp = self.session.delete(
            f"{BASE_URL}/transfers/{transfer_id}",
            headers=_headers({"Idempotency-Key": idem}),
            timeout=15,
        )
        # DELETE returns 200 on success; raise for others
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise requests.HTTPError(f"Delete transfer failed: {e}\nResponse body: {resp.text}") from e
        return resp.json()

    # ---------------- Exchange Rates ----------------
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> dict:
        """Fetch the latest exchange rate from `from_currency` to `to_currency`.

        Wrapper around GET /exchange_rates?from=<>&to<>
        Returns the parsed JSON body (expected to include a `rate` key).
        """
        params = {"from": from_currency.lower(), "to": to_currency.lower()}
        resp = self.session.get(f"{BASE_URL}/exchange_rates", headers=_headers(), params=params, timeout=15)
        resp.raise_for_status()
        return resp.json() 