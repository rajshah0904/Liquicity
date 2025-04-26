import os
import uuid
import asyncio
import logging
import re
from datetime import datetime, date, timezone
from typing import Dict, Any, Optional, List
from unittest.mock import MagicMock

from modern_treasury import ModernTreasury
from modern_treasury._base_client import APIStatusError, APIConnectionError, APITimeoutError

from app.payments.providers.base import PaymentProvider, BankAccount, TransactionResult

logger = logging.getLogger(__name__)

# Custom error class for testing
class MTAPIError(Exception):
    """Custom error class for testing Modern Treasury API errors"""
    def __init__(self, message, status_code=400, error_detail=None):
        super().__init__(message)
        self.status_code = status_code
        self.error_detail = error_detail or {}
    def json(self):
        return self.error_detail

class USPaymentRailType:
    ACH = "ach"
    WIRE = "wire"
    RTP = "rtp"
    FEDNOW = "fednow"
    VALID_TYPES = [ACH, WIRE, RTP, FEDNOW]

class MTTransactionResult(TransactionResult):
    def __init__(
        self,
        transaction_id: str,
        status: str,
        settled_at: Optional[datetime] = None,
        rail_used: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        amount: Optional[float] = None,
        currency: Optional[str] = None
    ):
        self.id = transaction_id
        self.transaction_id = transaction_id
        self.status = status
        self.settled_at = settled_at or datetime.now(timezone.utc)
        self.rail_used = rail_used
        self.rails = rail_used
        self.metadata = metadata or {}
        self.amount = amount
        self.currency = currency

class USBankAccount(BankAccount):
    def __init__(self, routing_number: str, account_number: str, account_type: str = "checking"):
        self.country_code = "US"
        self._validate_routing_number(routing_number)
        self._validate_account_number(account_number)
        self._validate_account_type(account_type)
        self.routing_number = routing_number
        self.account_number = account_number
        self.account_type = account_type

    def _validate_routing_number(self, routing_number: str) -> None:
        if not re.match(r'^\d{9}$', routing_number):
            raise ValueError("US routing number must be exactly 9 digits")
        digits = [int(d) for d in routing_number]
        checksum = (
            3 * (digits[0] + digits[3] + digits[6]) +
            7 * (digits[1] + digits[4] + digits[7]) +
            (digits[2] + digits[5] + digits[8])
        )
        if checksum % 10 != 0:
            raise ValueError("Invalid US routing number checksum")

    def _validate_account_number(self, account_number: str) -> None:
        if not re.match(r'^\d{4,17}$', account_number):
            raise ValueError("US account number must be between 4 and 17 digits")
    def _validate_account_type(self, account_type: str) -> None:
        if account_type not in ["checking", "savings"]:
            raise ValueError("account_type must be 'checking' or 'savings'")

class ModernTreasuryProvider(PaymentProvider):
    def __init__(self):
        api_key = os.getenv("MODERN_TREASURY_API_KEY")
        if not api_key:
            raise ValueError("MODERN_TREASURY_API_KEY environment variable is not set")
        org_id = os.getenv("MODERN_TREASURY_ORGANIZATION_ID") or os.getenv("MODERN_TREASURY_ORG_ID")
        if not org_id:
            raise ValueError("MODERN_TREASURY_ORGANIZATION_ID environment variable is not set")

        if os.getenv("TESTING") == "1":
            self.client = MagicMock()
        else:
            self.client = ModernTreasury(api_key=api_key, organization_id=org_id)

        self.default_originating_account_id = os.getenv("MODERN_TREASURY_DEFAULT_ACCOUNT_ID")
        self.max_retries = 3
        self.retry_delay = 1

        # ACH subtype must be a valid SEC code: CCD, PPD, IAT, CTX, WEB, CIE, TEL
        self.rail_configs = {
            "ach": {"default_subtype": "PPD"},
            "wire": {"default_priority": "high"},
            "rtp": {},
            "fednow": {},
        }

    async def pull(
        self,
        amount: float,
        currency: str,
        account: BankAccount,
        preferred_rail: str = USPaymentRailType.ACH,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TransactionResult:
        if currency.upper() != "USD":
            raise ValueError("US rails only support USD")
        if getattr(account, "country_code", "US") != "US":
            raise ValueError("US rails require a US BankAccount")

        idempotency_key = str(uuid.uuid4())
        cents = int(amount * 100)
        rail = preferred_rail if preferred_rail in USPaymentRailType.VALID_TYPES else USPaymentRailType.ACH

        params = {
            "type": rail,
            "amount": cents,
            "currency": "USD",
            "direction": "debit",
            "originating_account_id": self.default_originating_account_id,
            "description": f"{rail.upper()} debit of ${amount:.2f}",
        }

        recv_id = (metadata or {}).get("receiver_account_id") or (metadata or {}).get("counterparty_id")
        if recv_id:
            params["receiving_account_id"] = recv_id
        else:
            params["receiving_account"] = {
                "account_type": getattr(account, "account_type", "checking"),
                "routing_number": account.routing_number,
                "account_number": account.account_number,
                "country": "US",
                "party_name": (metadata or {}).get("note", "Test Recipient"),
            }

        if rail == USPaymentRailType.ACH:
            params["subtype"] = self.rail_configs["ach"]["default_subtype"]
        if metadata:
            params["metadata"] = metadata

        return await self._execute_with_retry("payment_order", params, idempotency_key)

    async def push(
        self,
        amount: float,
        currency: str,
        account: BankAccount,
        preferred_rail: str = USPaymentRailType.RTP,
        fallback_hierarchy: Optional[List[str]] = None,
        smart_rails: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TransactionResult:
        if currency.upper() != "USD":
            raise ValueError("US rails only support USD")
        if getattr(account, "country_code", "US") != "US":
            raise ValueError("US rails require a US BankAccount")

        idempotency_key = str(uuid.uuid4())
        cents = int(amount * 100)

        if smart_rails:
            if amount <= 100:
                preferred_rail = USPaymentRailType.RTP
            elif amount <= 25000:
                preferred_rail = USPaymentRailType.ACH
            else:
                preferred_rail = USPaymentRailType.WIRE

        rails = [preferred_rail] + (fallback_hierarchy or [r for r in USPaymentRailType.VALID_TYPES if r != preferred_rail])
        last_err = None

        for rail in rails:
            try:
                params = {
                    "type": rail,
                    "amount": cents,
                    "currency": "USD",
                    "direction": "credit",
                    "originating_account_id": self.default_originating_account_id,
                    "description": f"{rail.upper()} credit of ${amount:.2f}",
                }

                recv_id = (metadata or {}).get("receiver_account_id") or (metadata or {}).get("counterparty_id")
                if recv_id:
                    params["receiving_account_id"] = recv_id
                else:
                    params["receiving_account"] = {
                        "account_type": getattr(account, "account_type", "checking"),
                        "routing_number": account.routing_number,
                        "account_number": account.account_number,
                        "country": "US",
                        "party_name": (metadata or {}).get("note", "Test Recipient"),
                    }

                if rail == USPaymentRailType.ACH:
                    params["subtype"] = self.rail_configs["ach"]["default_subtype"]
                elif rail == USPaymentRailType.WIRE:
                    params["priority"] = self.rail_configs["wire"]["default_priority"]

                params.setdefault("metadata", {})
                if metadata:
                    params["metadata"].update(metadata)
                params["metadata"]["rail_used"] = rail

                res = await self._execute_with_retry("payment_order", params, f"{idempotency_key}-{rail}")
                if isinstance(res, MTTransactionResult):
                    res.rail_used = rail
                    res.rails = rail
                    res.amount = amount
                    res.currency = currency
                return res

            except APIStatusError as e:
                logger.warning(f"{rail.upper()} failed: {e}. Next.")
                last_err = e
                continue

        if last_err:
            logger.error(f"All rails failed: {last_err}")
            raise last_err
        raise ValueError("Failed to push via any rail")

    async def wire_transfer(
        self,
        amount: float,
        account: BankAccount,
        beneficiary_name: str,
        memo: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TransactionResult:
        idempotency_key = str(uuid.uuid4())
        cents = int(amount * 100)

        params = {
            "type": "wire",
            "amount": cents,
            "currency": "USD",
            "direction": "credit",
            "originating_account_id": self.default_originating_account_id,
            "description": f"Wire transfer of ${amount:.2f}",
            "priority": self.rail_configs["wire"]["default_priority"],
        }

        recv_id = (metadata or {}).get("receiver_account_id") or (metadata or {}).get("counterparty_id")
        if recv_id:
            params["receiving_account_id"] = recv_id
        else:
            params["receiving_account"] = {
                "account_type": getattr(account, "account_type", "checking"),
                "routing_number": account.routing_number,
                "account_number": account.account_number,
                "country": "US",
                "party_name": beneficiary_name,
            }

        if memo:
            params["remittance_information"] = memo
        if metadata:
            params["metadata"] = metadata

        res = await self._execute_with_retry("payment_order", params, idempotency_key)
        if isinstance(res, MTTransactionResult):
            res.amount = amount
            res.currency = "USD"
        return res

    async def same_day_ach(
        self,
        amount: float,
        account: BankAccount,
        is_push: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TransactionResult:
        if amount > 25000:
            raise ValueError("Same-day ACH limited to $25k")
        idempotency_key = str(uuid.uuid4())
        cents = int(amount * 100)

        params = {
            "type": "ach",
            "amount": cents,
            "currency": "USD",
            "direction": "credit" if is_push else "debit",
            "originating_account_id": self.default_originating_account_id,
            "subtype": "same_day",
            "description": f"Same-day ACH {'credit' if is_push else 'debit'} of ${amount:.2f}",
        }

        recv_id = (metadata or {}).get("receiver_account_id") or (metadata or {}).get("counterparty_id")
        if recv_id:
            params["receiving_account_id"] = recv_id
        else:
            params["receiving_account"] = {
                "account_type": getattr(account, "account_type", "checking"),
                "routing_number": account.routing_number,
                "account_number": account.account_number,
                "country": "US",
                "party_name": (metadata or {}).get("note", "Test Recipient"),
            }

        if metadata:
            params["metadata"] = metadata

        res = await self._execute_with_retry("payment_order", params, idempotency_key)
        if isinstance(res, MTTransactionResult):
            res.amount = amount
            res.currency = "USD"
            res.rails = "ach"
        return res

    async def fednow_transfer(
        self,
        amount: float,
        account: BankAccount,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TransactionResult:
        idempotency_key = str(uuid.uuid4())
        cents = int(amount * 100)

        params = {
            "type": "fednow",
            "amount": cents,
            "currency": "USD",
            "direction": "credit",
            "originating_account_id": self.default_originating_account_id,
            "description": f"FedNow instant payment of ${amount:.2f}",
        }

        recv_id = (metadata or {}).get("receiver_account_id") or (metadata or {}).get("counterparty_id")
        if recv_id:
            params["receiving_account_id"] = recv_id
        else:
            params["receiving_account"] = {
                "account_type": getattr(account, "account_type", "checking"),
                "routing_number": account.routing_number,
                "account_number": account.account_number,
                "country": "US",
                "party_name": (metadata or {}).get("note", "Test Recipient"),
            }

        if metadata:
            params["metadata"] = metadata

        res = await self._execute_with_retry("payment_order", params, idempotency_key)
        if isinstance(res, MTTransactionResult):
            res.amount = amount
            res.currency = "USD"
            res.rails = "fednow"
        return res

    async def _execute_with_retry(
        self, method_name: str, params: Dict[str, Any], idempotency_key: str
    ) -> MTTransactionResult:
        if os.getenv("TESTING") == "1":
            logger.info(f"TESTING mode – mocking {method_name}")
            mock_id = f"mt_{method_name}_{uuid.uuid4().hex[:8]}"
            rails = params.get("rails", params.get("type", "ach"))
            amt = params.get("amount", 0)
            cur = params.get("currency", "USD")
            return MTTransactionResult(
                transaction_id=mock_id,
                status="pending",
                settled_at=datetime.now(timezone.utc),
                rail_used=rails,
                metadata=params.get("metadata", {}),
                amount=amt / 100 if isinstance(amt, int) else amt,
                currency=cur,
            )

        retries = 0
        while retries <= self.max_retries:
            try:
                logger.info(f"API call ({method_name}): params={params}")
                response = await asyncio.to_thread(
                    self.client.payment_orders.create,
                    **params,
                    idempotency_key=idempotency_key
                )
                status_map = {
                    "approved": "pending",
                    "pending": "pending",
                    "completed": "completed",
                    "failed": "failed",
                    "returned": "failed",
                }
                status = status_map.get(response.status, "pending")
                settled = getattr(response, "effective_date", None)
                settled_at = self._parse_datetime(settled) if settled else None
                md = getattr(response, "metadata", {}) or {}
                return MTTransactionResult(
                    transaction_id=response.id,
                    status=status,
                    settled_at=settled_at,
                    rail_used=md.get("rail_used"),
                    metadata=md,
                    amount=params.get("amount", 0) / 100,
                    currency=params.get("currency"),
                )
            except (APIConnectionError, APITimeoutError) as e:
                retries += 1
                if retries <= self.max_retries:
                    wait = self.retry_delay * (2 ** (retries - 1))
                    logger.warning(f"Retry {retries}/{self.max_retries} after {e}, waiting {wait}s")
                    await asyncio.sleep(wait)
                else:
                    logger.error(f"Max retries reached: {e}")
                    raise
            except APIStatusError as e:
                logger.error(f"API status error: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                raise

    def _parse_datetime(self, date_str: Optional[Any]) -> Optional[datetime]:
        # If it's already a datetime, use it.
        if isinstance(date_str, datetime):
            return date_str
        # If it's a date, convert to datetime at midnight UTC.
        if isinstance(date_str, date):
            return datetime(date_str.year, date_str.month, date_str.day, tzinfo=timezone.utc)
        # If it's not a string, we can't parse it.
        if not isinstance(date_str, str):
            return None
        # Try ISO parsing first, then fallback to Z-terminated format.
        try:
            return datetime.fromisoformat(date_str)
        except ValueError:
            try:
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                return None
