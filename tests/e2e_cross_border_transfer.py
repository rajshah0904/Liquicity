import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.payments.services.orchestrator import transfer_cross_border

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Test environment variables
os.environ["TESTING"] = "1"  # Enable test mode for providers
os.environ["MODERN_TREASURY_API_KEY"] = "test_mt_key"
os.environ["MODERN_TREASURY_ORG_ID"] = "test_mt_org_id"
os.environ["RAPYD_ACCESS_KEY"] = "test_rapyd_access_key"
os.environ["RAPYD_SECRET_KEY"] = "test_rapyd_secret_key"
os.environ["TEST_US_ACCOUNT"] = "12345678"
os.environ["TEST_US_ROUTING"] = "021000021"
os.environ["TEST_US_ACCOUNT_TYPE"] = "checking"
os.environ["TEST_CA_ACCOUNT"] = "12345678"
os.environ["TEST_CA_ROUTING"] = "123456789"
os.environ["NODE_PATH"] = "node"

async def test_us_to_canada_transfer():
    """Test a cross-border transfer from US to Canada using Stargate as bridge."""
    logger.info("=== Testing US to Canada cross-border transfer ===")
    
    # Define test parameters
    metadata = {
        "reference": "us-ca-test-001",
        "bank_account_id": "test_bank_account_123",
        "purpose": "Test cross-border transfer via Stargate"
    }
    
    try:
        # Execute the cross-border transfer
        result = await transfer_cross_border(
            user_id="test_user_123",
            amount=100.0,
            src_cc="US",      # Source country: US (uses Modern Treasury)
            dst_cc="CA",      # Destination country: Canada (uses Rapyd)
            currency="USD",   # Currency: USD
            src_chain="1",    # Source chain: Ethereum
            dst_chain="137",  # Destination chain: Polygon
            metadata=metadata
        )
        
        # Log the result
        logger.info(f"Cross-border transfer completed with status: {result['status']}")
        
        # Print transaction IDs for each step
        if result["debit"]:
            logger.info(f"Debit transaction ID: {result['debit'].transaction_id}")
        
        if result["bridge_onramp"]:
            logger.info(f"Bridge onramp transaction ID: {result['bridge_onramp']['tx_id']}")
            logger.info(f"Bridge onramp status: {result['bridge_onramp']['status']}")
        
        if result["bridge_offramp"]:
            logger.info(f"Bridge offramp transaction ID: {result['bridge_offramp']['tx_id']}")
            logger.info(f"Bridge offramp status: {result['bridge_offramp']['status']}")
        
        if result["payout"]:
            logger.info(f"Payout transaction ID: {result['payout'].transaction_id}")
        
        # Check for errors
        if result["errors"]:
            logger.error("Errors occurred during the transfer:")
            for err in result["errors"]:
                logger.error(f"  - {err}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error during test_us_to_canada_transfer: {str(e)}")
        raise

async def test_us_to_nigeria_transfer():
    """Test a cross-border transfer from US to Nigeria using Stargate as bridge."""
    logger.info("=== Testing US to Nigeria cross-border transfer ===")
    
    # Define test parameters
    metadata = {
        "reference": "us-ng-test-001",
        "bank_account_id": "test_bank_account_456",
        "purpose": "Test cross-border transfer via Stargate"
    }
    
    try:
        # Execute the cross-border transfer
        result = await transfer_cross_border(
            user_id="test_user_456",
            amount=50.0,
            src_cc="US",      # Source country: US (uses Modern Treasury)
            dst_cc="NG",      # Destination country: Nigeria (uses Rapyd)
            currency="USD",   # Currency: USD
            src_chain="1",    # Source chain: Ethereum
            dst_chain="137",  # Destination chain: Polygon
            metadata=metadata
        )
        
        # Log the result
        logger.info(f"Cross-border transfer completed with status: {result['status']}")
        
        # Print transaction IDs for each step
        if result["debit"]:
            logger.info(f"Debit transaction ID: {result['debit'].transaction_id}")
        
        if result["bridge_onramp"]:
            logger.info(f"Bridge onramp transaction ID: {result['bridge_onramp']['tx_id']}")
            logger.info(f"Bridge onramp status: {result['bridge_onramp']['status']}")
        
        if result["bridge_offramp"]:
            logger.info(f"Bridge offramp transaction ID: {result['bridge_offramp']['tx_id']}")
            logger.info(f"Bridge offramp status: {result['bridge_offramp']['status']}")
        
        if result["payout"]:
            logger.info(f"Payout transaction ID: {result['payout'].transaction_id}")
        
        # Check for errors
        if result["errors"]:
            logger.error("Errors occurred during the transfer:")
            for err in result["errors"]:
                logger.error(f"  - {err}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error during test_us_to_nigeria_transfer: {str(e)}")
        raise

async def run_tests():
    """Run all test cases."""
    logger.info("Starting cross-border transfer tests")
    
    # Test US to Canada transfer
    try:
        us_to_ca_result = await test_us_to_canada_transfer()
        logger.info(f"US to Canada test completed with status: {us_to_ca_result['status']}")
    except Exception as e:
        logger.error(f"US to Canada test failed: {str(e)}")
    
    # Test US to Nigeria transfer
    try:
        us_to_ng_result = await test_us_to_nigeria_transfer()
        logger.info(f"US to Nigeria test completed with status: {us_to_ng_result['status']}")
    except Exception as e:
        logger.error(f"US to Nigeria test failed: {str(e)}")
    
    logger.info("All tests completed")

if __name__ == "__main__":
    # Run the test suite
    asyncio.run(run_tests()) 