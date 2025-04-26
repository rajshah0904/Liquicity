import os
from typing import Any, Dict, Optional
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

async def send_fiat(
    user_id: str, 
    amount: float, 
    currency: str, 
    country_code: str = "CA",
    refund: bool = False,
    metadata: Optional[Dict[str, Any]] = None
) -> Any:
    """
    Credit funds to the user's bank, or refund if refund=True.
    
    Args:
        user_id: ID of the user
        amount: Amount to transfer
        currency: Currency code
        country_code: Destination country code (default: CA)
        refund: Whether this is a refund (default: False)
        metadata: Additional metadata for the transaction
        
    Returns:
        The result of the payment operation
    """
    # Construct metadata
    combined_metadata = {"user_id": user_id, "refund": refund}
    if metadata:
        # Make sure metadata is a flat dictionary with string keys and simple values
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                combined_metadata[key] = value
    
    # Convert country to uppercase
    country = country_code.upper()
    
    # Configure destination bank account based on country
    if country == "CA":
        acct = InternationalBankAccount(
            routing_number=os.getenv("TEST_CA_ROUTING"),
            account_number=os.getenv("TEST_CA_ACCOUNT"),
            country=SupportedCountries.CANADA,
            account_holder_name=os.getenv("TEST_CA_ACCOUNT_HOLDER", "Test User")
        )
    elif country == "NG":
        acct = InternationalBankAccount(
            routing_number=os.getenv("TEST_NG_ROUTING", "123456789"),
            account_number=os.getenv("TEST_NG_ACCOUNT", "1234567890"),
            country=SupportedCountries.NIGERIA,
            account_holder_name=os.getenv("TEST_NG_ACCOUNT_HOLDER", "Test User")
        )
    elif country == "MX":
        acct = InternationalBankAccount(
            routing_number=os.getenv("TEST_MX_ROUTING", "123456789012345678"),
            account_number=os.getenv("TEST_MX_ACCOUNT", "123456789012345678"),
            country=SupportedCountries.MEXICO,
            account_holder_name=os.getenv("TEST_MX_ACCOUNT_HOLDER", "Test User")
        )
    else:
        # Default to Canadian account for unsupported countries
        acct = InternationalBankAccount(
            routing_number=os.getenv("TEST_CA_ROUTING"),
            account_number=os.getenv("TEST_CA_ACCOUNT"),
            country=SupportedCountries.CANADA,
            account_holder_name=os.getenv("TEST_CA_ACCOUNT_HOLDER", "Test User")
        )
    
    # Get the provider for the destination country
    provider = get_provider(country)
    
    # Execute the payment
    return await provider.push(
        amount, currency, acct, metadata=combined_metadata
    ) 