#!/usr/bin/env python
"""
Sandbox test for Modern Treasury domestic transfers.

This script tests US domestic transfers using the Modern Treasury provider
in REAL SANDBOX MODE (not mocked responses). It tests all three payment rails:
- ACH
- RTP
- Wire Transfer
"""

import os
import sys
import logging
import asyncio
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.payments.services.orchestrator import transfer_domestic
from app.payments.providers.modern_treasury import USPaymentRailType

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set to 0 to use the real sandbox API (not mocked responses)
os.environ["TESTING"] = "0"

# Set Modern Treasury sandbox credentials
os.environ["MODERN_TREASURY_API_KEY"] = "test-tok_12345678"  # Replace with your real sandbox API key
os.environ["MODERN_TREASURY_ORG_ID"] = "org_12345678"        # Replace with your real sandbox org ID
os.environ["MODERN_TREASURY_DEFAULT_ACCOUNT_ID"] = "ext_account_12345678"  # Replace with your sandbox account ID

# US bank account for testing - must use valid routing number with valid checksum
os.environ["TEST_US_ACCOUNT"] = "123456789"
os.environ["TEST_US_ROUTING"] = "021000021"  # Chase routing number (valid checksum)
os.environ["TEST_US_ACCOUNT_TYPE"] = "checking"

# Define test scenarios
TEST_SCENARIOS = [
    # Format: (description, rail, amount)
    ("US Domestic ACH Transfer", USPaymentRailType.ACH, 100.0),
    ("US Domestic RTP Transfer", USPaymentRailType.RTP, 50.0),
    ("US Domestic Wire Transfer", USPaymentRailType.WIRE, 150.0),
]

async def test_mt_domestic_transfer(description: str, rail: str, amount: float) -> None:
    """Test a domestic transfer using Modern Treasury in sandbox mode"""
    logger.info(f"=== Testing {description} ===")
    
    # Generate a unique user ID and reference for this test
    timestamp = int(datetime.now().timestamp())
    user_id = f"test_user_mt_{timestamp}"
    
    # Set up metadata with descriptive fields for tracking in the sandbox dashboard
    metadata = {
        "purpose": "Testing Modern Treasury domestic transfer",
        "description": description,
        "payment_rail": rail,
        "test_id": f"mt_test_{timestamp}",
        "customer_name": "Harry Potter",
        "account_name": "Gringotts Vault 713"
    }
    
    try:
        # Execute the domestic transfer
        result = await transfer_domestic(
            user_id=user_id,
            amount=amount,
            country_code="US",
            currency="USD",
            preferred_rail=rail,
            metadata=metadata
        )
        
        # Log detailed results
        logger.info(f"Domestic transfer completed with status: {result['status']}")
        
        if result["debit"]:
            logger.info(f"Debit transaction ID: {result['debit'].transaction_id}")
            logger.info(f"Debit status: {result['debit'].status}")
        
        if result["payout"]:
            logger.info(f"Payout transaction ID: {result['payout'].transaction_id}")
            logger.info(f"Payout status: {result['payout'].status}")
            if hasattr(result["payout"], "rails"):
                logger.info(f"Payment rail used: {result['payout'].rails}")
        
        logger.info(f"{description} test completed with status: {result['status']}")
        
    except Exception as e:
        logger.error(f"Error during {description}: {str(e)}", exc_info=True)
        logger.info(f"{description} test failed with error")

async def run_tests() -> None:
    """Run all Modern Treasury domestic transfer test scenarios"""
    logger.info("Starting Modern Treasury domestic transfer tests in SANDBOX mode")
    
    for description, rail, amount in TEST_SCENARIOS:
        await test_mt_domestic_transfer(description, rail, amount)
        
        # Add a delay between tests
        await asyncio.sleep(2)
    
    logger.info("All Modern Treasury domestic transfer tests completed")

if __name__ == "__main__":
    try:
        asyncio.run(run_tests())
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}", exc_info=True) 