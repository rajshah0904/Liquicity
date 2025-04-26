#!/usr/bin/env python
"""
End-to-end test for the unified money transfer service.

This script tests both domestic and cross-border transfers through
the unified transfer_money service that automatically chooses the
optimal transfer method based on source and destination countries.
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.payments.services.transfer_service import transfer_money
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

# Define test scenarios - both domestic and cross-border
TEST_SCENARIOS = [
    # Format: (description, src_country, dst_country, amount, preferred_rail)
    # Domestic transfers
    ("US Domestic ACH Transfer", "US", "US", 100.0, USPaymentRailType.ACH),
    ("US Domestic RTP Transfer", "US", "US", 50.0, USPaymentRailType.RTP),
    ("Canadian Domestic Transfer", "CA", "CA", 75.0, None),
    ("Nigerian Domestic Transfer", "NG", "NG", 45.0, None),
    
    # Cross-border transfers
    ("US to Canada Transfer", "US", "CA", 85.0, None),
    ("Canada to US Transfer", "CA", "US", 65.0, None),
    ("Nigeria to Mexico Transfer", "NG", "MX", 55.0, None),
]

async def test_transfer(
    description: str, 
    src_country: str, 
    dst_country: str, 
    amount: float, 
    rail: str = None
) -> Dict[str, Any]:
    """Test a money transfer between two countries (may be domestic or cross-border)"""
    logger.info(f"=== Testing {description} ===")
    
    # Generate a unique user ID for this test
    user_id = f"test_user_{src_country}_{dst_country}_{int(datetime.now().timestamp())}"
    
    # Set up metadata
    metadata = {
        "purpose": "Testing unified transfer service",
        "description": description,
        "test_id": f"{src_country}_{dst_country}_{int(datetime.now().timestamp())}"
    }
    
    # Determine currency based on country
    if src_country == "NG":
        currency = "NGN"
    elif src_country == "CA":
        currency = "CAD"
    else:
        currency = "USD"
    
    # Execute the transfer through the unified service
    result = await transfer_money(
        user_id=user_id,
        amount=amount,
        src_cc=src_country,
        dst_cc=dst_country,
        currency=currency,
        preferred_rail=rail,
        metadata=metadata
    )
    
    # Log results
    logger.info(f"Transfer completed with status: {result['status']}")
    
    if result.get("debit"):
        logger.info(f"Debit transaction ID: {result['debit'].transaction_id}")
    
    # Log bridge information for cross-border transfers
    if src_country != dst_country:
        if result.get("bridge_onramp"):
            if isinstance(result["bridge_onramp"], dict):
                logger.info(f"Bridge onramp tx ID: {result['bridge_onramp'].get('tx_id')}")
            else:
                logger.info(f"Bridge onramp tx ID: {getattr(result['bridge_onramp'], 'tx_id', 'unknown')}")
            
        if result.get("bridge_offramp"):
            if isinstance(result["bridge_offramp"], dict):
                logger.info(f"Bridge offramp tx ID: {result['bridge_offramp'].get('tx_id')}")
            else:
                logger.info(f"Bridge offramp tx ID: {getattr(result['bridge_offramp'], 'tx_id', 'unknown')}")
    
    if result.get("payout"):
        logger.info(f"Payout transaction ID: {result['payout'].transaction_id}")
    
    logger.info(f"{description} test completed with status: {result['status']}")
    
    return result

async def run_tests() -> List[Tuple[str, str]]:
    """Run all transfer test scenarios"""
    logger.info("Starting unified transfer tests for both domestic and cross-border scenarios")
    
    results = []
    for description, src, dst, amount, rail in TEST_SCENARIOS:
        try:
            result = await test_transfer(description, src, dst, amount, rail)
            results.append((description, result["status"]))
        except Exception as e:
            logger.error(f"Error during {description}: {str(e)}", exc_info=True)
            results.append((description, "error"))
        
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