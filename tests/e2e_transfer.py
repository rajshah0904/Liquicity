#!/usr/bin/env python3
import os, sys, asyncio
# Add project root to Python path so `import app` resolves correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.payments.services.orchestrator import transfer_cross_border
from app.payments.providers.rapyd import RapydProvider, InternationalBankAccount, SupportedCountries
from app.payments.services.payment_service import send_fiat
from unittest.mock import patch, MagicMock
from datetime import datetime

# Ensure sandbox environment variables are set before running
required = [
    "MODERN_TREASURY_DEFAULT_ACCOUNT_ID",
    "MODERN_TREASURY_API_KEY",
    "MODERN_TREASURY_ORG_ID",
    "RAPYD_ACCESS_KEY",
    "RAPYD_SECRET_KEY",
    "CIRCLE_API_KEY",
    "TEST_US_ACCOUNT",
    "TEST_US_ROUTING",
]
missing = [k for k in required if not os.getenv(k)]
if missing:
    print(f"Error: missing environment variables: {missing}", file=sys.stderr)
    sys.exit(1)

# REMOVE TESTING FLAG - we want real sandbox API calls
os.environ["TESTING"] = "1"

async def main():
    print("Setting up Rapyd sandbox test account (REAL API MODE)...")
    
    # Initialize Rapyd provider
    rp = RapydProvider()

    # 1. Create a sandbox ewallet
    print("Creating Rapyd wallet...")
    ew = await rp.create_ewallet(
        first_name="Harry",
        last_name="Potter",
        email="harry@hogwarts.com",
        ewallet_reference_id=f"hp_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        contact={
            "phone_number": "+14155550123",
            "email": "test.user@example.com",
            "first_name": "Test",
            "last_name": "User",
            "address": {
                "name": "Test User",
                "line_1": "123 Main Street",
                "city": "Anytown",
                "state": "NY",
                "country": "US",
                "zip": "12345",
                "phone_number": "+14155550123"
            },
            "identification_type": "PA",
            "identification_number": "A123456789",
            "date_of_birth": "1990-01-01",
            "country": "US",
            "nationality": "US"
        }
    )
    
    ewallet_id = ew["data"]["id"]
    print(f"Created ewallet {ewallet_id}")

    # 2. Issue a virtual CAD account
    print("Creating virtual CAD account...")
    vb = await rp.create_virtual_account(
        ewallet_id=ewallet_id,
        currency="CAD",
        country="CA",
        description="Harry's Test Account"
    )
    
    # Extract the account details for use in the transfer
    virtual_account = vb["data"]
    account_id = virtual_account["id"]
    account_number = virtual_account["bank_account"]["account_number"]
    routing_number = virtual_account["bank_account"]["bank_code"]
    
    print(f"Created virtual account {account_id}")
    print(f"Account number: {account_number}")
    print(f"Routing number: {routing_number}")

    # 3. Simulate funding
    print("Funding virtual account with test CAD...")
    tf = await rp.simulate_bank_transfer(
        issued_bank_account_id=account_id,
        amount=100000,  # in minor units, e.g. 1000.00 CAD = 100000
        currency="CAD"
    )
    print(f"Funded account with 1000.00 CAD")

    # Create Canadian account object with the virtual account details
    ca_account = InternationalBankAccount(
        routing_number=routing_number,
        account_number=account_number,
        country=SupportedCountries.CANADA,
        account_holder_name="Harry Potter",
        bank_name=virtual_account["bank_account"]["bank_name"]
    )

    # 4. Create a custom bank transfer implementation that uses the virtual account
    async def custom_send_fiat_to_virtual(user_id, amount, currency):
        from app.payments.providers.factory import get_provider
        provider = get_provider("CA")
        return await provider.push(
            amount, currency, ca_account, metadata={"virtual_account_id": account_id}
        )

    # 5. Run the cross-border transfer with our destination account
    # Only patch the send_fiat function to use our virtual account
    with patch('app.payments.services.orchestrator.send_fiat', custom_send_fiat_to_virtual):
        print("\nStarting cross-border transfer...")
        result = await transfer_cross_border(
            user_id="cli_user",
            amount=5.00,  # Transfer $5 USD
            src_cc="US",
            dst_cc="CA",
            currency="USD",
            chain="polygon",
            metadata={
                "note": "Transfer to Harry Potter's virtual Rapyd account",
                "counterparty_id": "ad2a0a1c-dd82-4d7e-94b7-b07df0376e9e"
            }
        )
        print("\nTransfer completed!")
        print(result)

if __name__ == "__main__":
    asyncio.run(main())