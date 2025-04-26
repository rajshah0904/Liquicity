#!/usr/bin/env python
"""
End-to-end test for cross-border transfers between all country combinations.

This script tests transfers between:
1. International → US (Rapyd → Stargate → ModernTreasury)
2. International → Different International (Rapyd → Stargate → Rapyd)
3. US → International (ModernTreasury → Stargate → Rapyd) - already tested

Tests are run using the orchestrator service, which coordinates between
different payment providers and cross-chain bridge operations.
"""

import os
import sys
import logging
import asyncio
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.payments.services.orchestrator import transfer_cross_border

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set test environment flag
os.environ["TESTING"] = "1"

# Set test account information for various countries
# US accounts (Modern Treasury)
os.environ["TEST_US_ACCOUNT"] = "123456789"
os.environ["TEST_US_ROUTING"] = "021000021"  # Chase routing number (valid checksum)
os.environ["TEST_US_ACCOUNT_TYPE"] = "checking"

# Canadian accounts (Rapyd)
os.environ["TEST_CA_ROUTING"] = "11000-000"
os.environ["TEST_CA_ACCOUNT"] = "12345678"
os.environ["TEST_CA_ACCOUNT_HOLDER"] = "Canadian Test User"

# Nigerian accounts (Rapyd)
os.environ["TEST_NG_ROUTING"] = "123456789"
os.environ["TEST_NG_ACCOUNT"] = "1234567890"  # 10-digit NUBAN
os.environ["TEST_NG_ACCOUNT_HOLDER"] = "Nigerian Test User"

# Mexican accounts (Rapyd)
os.environ["TEST_MX_ROUTING"] = "123456789012345678"  # 18-digit CLABE
os.environ["TEST_MX_ACCOUNT"] = "123456789012345678"
os.environ["TEST_MX_ACCOUNT_HOLDER"] = "Mexican Test User"

# Define test data
TEST_COMBINATIONS = [
    # Format: (description, source_country, destination_country, amount)
    ("Canada to US", "CA", "US", 75.0),
    ("Nigeria to US", "NG", "US", 60.0),
    ("Mexico to Canada", "MX", "CA", 55.0),
    ("Canada to Nigeria", "CA", "NG", 45.0),
    ("Nigeria to Mexico", "NG", "MX", 65.0),
]

async def test_combination(description, src_cc, dst_cc, amount):
    """Run a single cross-border transfer test between two countries"""
    logger.info(f"=== Testing {description} cross-border transfer ===")
    
    # Generate a unique user ID for this test
    user_id = f"test_user_{src_cc}_{dst_cc}_{int(datetime.now().timestamp())}"
    
    # Set up transaction metadata
    metadata = {
        "purpose": "Testing cross-border transfer",
        "description": description,
        "source_country": src_cc,
        "destination_country": dst_cc,
        "test_id": f"{src_cc}_{dst_cc}_{int(datetime.now().timestamp())}"
    }
    
    # Execute the cross-border transfer
    result = await transfer_cross_border(
        user_id=user_id,
        amount=amount,
        src_cc=src_cc,
        dst_cc=dst_cc,
        currency="USD",  # Using USD for all tests
        src_chain="137",     # Using Polygon for all tests
        metadata=metadata
    )
    
    # Log the results
    logger.info(f"Cross-border transfer completed with status: {result['status']}")
    
    if result["debit"]:
        logger.info(f"Debit transaction ID: {result['debit'].transaction_id}")
    
    if result["bridge_onramp"]:
        if isinstance(result["bridge_onramp"], dict):
            logger.info(f"Bridge onramp transaction ID: {result['bridge_onramp'].get('tx_id')}")
            logger.info(f"Bridge onramp status: {result['bridge_onramp'].get('status')}")
        else:
            logger.info(f"Bridge onramp transaction ID: {getattr(result['bridge_onramp'], 'tx_id', 'unknown')}")
            logger.info(f"Bridge onramp status: {getattr(result['bridge_onramp'], 'status', 'unknown')}")
    
    if result["bridge_offramp"]:
        if isinstance(result["bridge_offramp"], dict):
            logger.info(f"Bridge offramp transaction ID: {result['bridge_offramp'].get('tx_id')}")
            logger.info(f"Bridge offramp status: {result['bridge_offramp'].get('status')}")
        else:
            logger.info(f"Bridge offramp transaction ID: {getattr(result['bridge_offramp'], 'tx_id', 'unknown')}")
            logger.info(f"Bridge offramp status: {getattr(result['bridge_offramp'], 'status', 'unknown')}")
    
    if result["payout"]:
        logger.info(f"Payout transaction ID: {result['payout'].transaction_id}")
    
    logger.info(f"{description} test completed with status: {result['status']}")
    
    # Return the result for potential further analysis
    return result

async def run_tests():
    """Run all test combinations"""
    logger.info("Starting cross-border transfer tests for all country combinations")
    
    results = []
    for test_data in TEST_COMBINATIONS:
        result = await test_combination(*test_data)
        results.append((test_data, result))
        
        # Add a small delay between tests
        await asyncio.sleep(1)
    
    # Summary
    logger.info("\n=== Test Summary ===")
    for (description, _, _, _), result in results:
        status = result["status"]
        logger.info(f"{description}: {status}")
    
    return results

if __name__ == "__main__":
    try:
        asyncio.run(run_tests())
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}", exc_info=True) 