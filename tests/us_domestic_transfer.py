#!/usr/bin/env python3
"""
Asynchronous test script for Modern Treasury API connection,
following the official Python SDK "Getting Started" guide.
"""
import os
import asyncio
import logging
import uuid
import sys
from decimal import Decimal
from typing import Dict, Any

import modern_treasury
from modern_treasury import AsyncModernTreasury

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Set the sandbox environment variables
os.environ["TESTING"] = "0"  # Use real sandbox mode
os.environ["MODERN_TREASURY_API_KEY"] = "test-Syoh2vUJS5H86XWTLYpNB5dCpRRuYYoFxGcB1wx2MNn3KTfkMgwsiJ4Z4Tf14mXt"
os.environ["MODERN_TREASURY_ORGANIZATION_ID"] = "45a1f03f-952a-4bc3-83ff-503381d3e831"
os.environ["MODERN_TREASURY_DEFAULT_ACCOUNT_ID"] = "26abae0c-04a4-4c7a-b147-5fcb2a12685e"  # Gringotts (TerraFlow) account ID

# Add parent directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.payments.providers.modern_treasury import ModernTreasuryProvider, USBankAccount

print(f"Running in SANDBOX mode with real API calls")

async def run_tests():
    # Initialize provider with the configured environment variables
    provider = ModernTreasuryProvider()

    # Create a bank account object for Harry Potter using details from the image
    destination_account = USBankAccount(
        routing_number="121141822",  # Harry's Bank of America routing number
        account_number="123456789",  # Harry's account number
        account_type="checking"      # Harry's account type
    )
    # country_code is automatically set to "US" in USBankAccount

    # Common transaction metadata
    transaction_id = str(uuid.uuid4())
    metadata = {
        "order_id": transaction_id,
        "customer_id": "harry_potter_5770f026",
        "description": "Transfer from Gringotts to Harry Potter",
        "sender_account_id": "26abae0c-04a4-4c7a-b147-5fcb2a12685e",
        "receiver_account_id": "5770f026-6b49-4160-826a-219aba4c83c0"
    }

    # Test ACH push
    try:
        print("\nTesting ACH push transfer...")
        ach_result = await provider.push(
            amount=100.00,
            currency="USD",
            account=destination_account,
            preferred_rail="ach",
            metadata=metadata
        )
        print(f"ACH Push Success: {ach_result}")
    except Exception as e:
        print(f"ACH Push Error: {str(e)}")

    # Test RTP push
    try:
        print("\nTesting RTP push transfer...")
        rtp_result = await provider.push(
            amount=150.00,
            currency="USD",
            account=destination_account,
            preferred_rail="rtp",
            metadata=metadata
        )
        print(f"RTP Push Success: {rtp_result}")
    except Exception as e:
        print(f"RTP Push Error: {str(e)}")

    # Test wire transfer
    try:
        print("\nTesting wire transfer...")
        wire_result = await provider.wire_transfer(
            amount=200.00,
            account=destination_account,
            beneficiary_name="Harry Potter",
            memo="Transfer from Gringotts Bank",
            metadata=metadata
        )
        print(f"Wire Transfer Success: {wire_result}")
    except Exception as e:
        print(f"Wire Transfer Error: {str(e)}")

    print("\nAll tests completed!")

async def test_sdk_connection():
    # Your sandbox credentials from the API key panel
    api_key = "test-Syoh2vUJS5H86XWTLYpNB5dCpRRuYYoFxGcB1wx2MNn3KTfkMgwsiJ4Z4Tf14mXt"
    org_id = "45a1f03f-952a-4bc3-83ff-503381d3e831"

    # Make them available to the SDK (optional if you pass them into the constructor)
    os.environ["MODERN_TREASURY_API_KEY"] = api_key
    os.environ["MODERN_TREASURY_ORGANIZATION_ID"] = org_id

    logger.info("=== Modern Treasury API Connection Test ===")
    logger.info(f"API Key (masked): {api_key[:8]}...{api_key[-4:]}")
    logger.info(f"Organization ID:   {org_id}")

    # Instantiate the async client (will pick up env vars by default)
    client = AsyncModernTreasury(
        api_key=api_key,
        organization_id=org_id
    )

    try:
        logger.info("Making API call to list payment orders...")
        response = await client.payment_orders.list()
        count = len(response.data) if hasattr(response, "data") else 0
        logger.info("API call successful!")
        logger.info(f"Found {count} payment orders")

        # Print SDK and endpoint info
        logger.info("\nAPI connection details:")
        logger.info(f"SDK Version: {modern_treasury.__version__}")
        logger.info(f"Base URL:    {getattr(client, '_base_url', 'Unknown')}")
    except Exception as e:
        logger.error(f"API call failed: {type(e).__name__}: {e}")
        if hasattr(e, "response") and hasattr(e.response, "text"):
            logger.error(f"Response body: {e.response.text}")
        logger.error("\nClient debug info:")
        logger.error(f"Client type: {type(client)}")
    finally:
        # Cleanly close the underlying HTTPX client
        await client.close()

async def main():
    # Run both tests
    await test_sdk_connection()
    await run_tests()

if __name__ == "__main__":
    asyncio.run(main())
