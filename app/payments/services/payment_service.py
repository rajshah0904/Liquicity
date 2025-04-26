import os
from typing import Any
from app.payments.providers.factory import get_provider
from app.payments.providers.modern_treasury import USBankAccount, USPaymentRailType
from app.payments.providers.rapyd import InternationalBankAccount, SupportedCountries

async def receive_fiat(user_id: str, amount: float, currency: str) -> Any:
    """
    Debit funds from the user's bank account (default: US ACH via Modern Treasury).
    """
    # Construct a test US bank account from env vars
    acct = USBankAccount(
        account_number=os.getenv("TEST_US_ACCOUNT"),
        routing_number=os.getenv("TEST_US_ROUTING"),
        account_type=os.getenv("TEST_US_ACCOUNT_TYPE", "checking")
    )
    provider = get_provider("US")
    return await provider.pull(
        amount,
        currency,
        acct,
        preferred_rail=os.getenv("DEFAULT_US_PULL_RAIL", USPaymentRailType.RTP),
    )

async def send_fiat(user_id: str, amount: float, currency: str, refund: bool = False) -> Any:
    """
    Credit funds to the user's bank (default: Canada via Rapyd), or refund if refund=True.
    """
    # Construct a test Canadian bank account from env vars
    acct = InternationalBankAccount(
        routing_number=os.getenv("TEST_CA_ROUTING"),
        account_number=os.getenv("TEST_CA_ACCOUNT"),
        country=SupportedCountries.CANADA
    )
    provider = get_provider("CA")
    return await provider.push(
        amount, currency, acct, metadata={"refund": refund}
    ) 