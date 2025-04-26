#!/usr/bin/env python
"""
End-to-end test for domestic transfers across all supported countries.

This script tests domestic transfers within:
1. US (using ModernTreasuryProvider)
2. Canada (using RapydProvider)  
3. Mexico (using RapydProvider)
4. Nigeria (using RapydProvider)

These domestic transfers bypass the blockchain bridge and directly use
the country's payment provider for both debit and credit operations.
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.payments.services.orchestrator import transfer_domestic
from app.payments.providers.modern_treasury import USPaymentRailType

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

# Define test scenarios
TEST_SCENARIOS = [
    # Format: (description, country_code, amount, preferred_rail)
    ("US Domestic ACH Transfer", "US", 100.0, USPaymentRailType.ACH),
    ("US Domestic RTP Transfer", "US", 50.0, USPaymentRailType.RTP),
    ("US Domestic Wire Transfer", "US", 150.0, USPaymentRailType.WIRE),
    ("Canadian Domestic Transfer", "CA", 75.0, None),
    ("Mexican Domestic Transfer", "MX", 60.0, None),
    ("Nigerian Domestic Transfer", "NG", 45.0, None),
]

async def test_domestic_transfer(description: str, country: str, amount: float, rail: str = None) -> Dict[str, Any]:
    """Test a domestic transfer within a single country"""
    logger.info(f"=== Testing {description} ===")
    
    # Generate a unique user ID for this test
    user_id = f"test_user_domestic_{country}_{int(datetime.now().timestamp())}"
    
    # Set up metadata
    metadata = {
        "purpose": "Testing domestic transfer",
        "description": description,
        "country": country,
        "test_id": f"domestic_{country}_{int(datetime.now().timestamp())}"
    }
    
    # Execute the domestic transfer
    result = await transfer_domestic(
        user_id=user_id,
        amount=amount,
        country_code=country,
        currency="USD" if country in ["US", "MX"] else "CAD" if country == "CA" else "NGN",
        preferred_rail=rail,
        metadata=metadata
    )
    
    # Log results
    logger.info(f"Domestic transfer completed with status: {result['status']}")
    
    if result["debit"]:
        logger.info(f"Debit transaction ID: {result['debit'].transaction_id}")
    
    if result["payout"]:
        logger.info(f"Payout transaction ID: {result['payout'].transaction_id}")
    
    logger.info(f"{description} test completed with status: {result['status']}")
    
    return result

async def run_tests() -> List[Tuple[str, str]]:
    """Run all domestic transfer test scenarios"""
    logger.info("Starting domestic transfer tests across all supported countries")
    
    results = []
    for description, country, amount, rail in TEST_SCENARIOS:
        result = await test_domestic_transfer(description, country, amount, rail)
        results.append((description, result["status"]))
        
        # Add a small delay between tests
        await asyncio.sleep(1)
    
    # Summary
    logger.info("\n=== Test Summary ===")
    for description, status in results:
        logger.info(f"{description}: {status}")
    
    return results

if __name__ == "__main__":
    try:
        asyncio.run(run_tests())
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}", exc_info=True) 