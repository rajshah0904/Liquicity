"""
Payment orchestration service for TerraFlow.

This module provides high-level orchestration of payment flows,
coordinating between different payment providers and stablecoin operations.
"""

import logging
from typing import Dict, Any, Optional

from .payment_service import receive_fiat, send_fiat
from ..providers.factory import get_stablecoin_provider

logger = logging.getLogger(__name__)

async def transfer_cross_border(
    user_id: str,
    amount: float,
    src_cc: str,
    dst_cc: str,
    currency: str,
    chain: str = "polygon",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute a cross-border transfer using stablecoins as an intermediary.
    
    This orchestrates a complete flow from source fiat currency to destination fiat currency,
    using stablecoins (USDC) as a bridge for the cross-border transfer.
    
    Flow:
    1. Pull funds from user's local payment source
    2. Mint USDC with the fiat amount
    3. Transfer USDC on-chain (handled internally by Circle)
    4. Redeem USDC to destination fiat
    5. Pay out to the recipient
    
    Args:
        user_id: ID of the user initiating the transfer
        amount: Amount to transfer
        src_cc: Source country code
        dst_cc: Destination country code
        currency: Currency to use (e.g., "USD")
        chain: Blockchain to use for the transfer (default: "polygon")
        metadata: Optional additional data for the transaction
        
    Returns:
        A dictionary with the results of each step
        
    Raises:
        ValueError: If any part of the transfer fails
    """
    result = {
        "debit": None,
        "mint": None, 
        "redeem": None,
        "payout": None,
        "status": "pending",
        "errors": []
    }
    
    try:
        # Step 1: Pull local fiat from user's payment source
        logger.info(f"Initiating fiat debit for user {user_id}, amount {amount} {currency}")
        result["debit"] = await receive_fiat(user_id, amount, currency)
        
        # Step 2: Mint USDC with the received fiat
        logger.info(f"Minting {amount} USDC on {chain} chain")
        sc = get_stablecoin_provider()
        result["mint"] = await sc.mint(amount, currency, chain, metadata)
        
        # Step 3: Transfer on-chain (handled internally by Circle mint operation)
        logger.info(f"On-chain transfer complete with transaction ID: {result['mint'].tx_id}")
        
        # Step 4: Redeem USDC to destination fiat
        logger.info(f"Redeeming USDC to fiat in destination country {dst_cc}")
        result["redeem"] = await sc.redeem(amount, currency, dst_cc, metadata)
        
        # Step 5: Pay out to the recipient
        logger.info(f"Sending fiat payout of {amount} {currency}")
        result["payout"] = await send_fiat(user_id, amount, currency)
        
        result["status"] = "completed"
        return result
        
    except Exception as e:
        logger.error(f"Error during cross-border transfer: {str(e)}")
        result["status"] = "failed"
        result["errors"].append(str(e))
        
        # Attempt fallback and recovery based on where the failure occurred
        try:
            await _handle_transfer_fallback(result, user_id, amount, currency)
        except Exception as fallback_error:
            logger.error(f"Fallback handling failed: {str(fallback_error)}")
            result["errors"].append(f"Fallback error: {str(fallback_error)}")
            
        return result

async def _handle_transfer_fallback(
    result: Dict[str, Any],
    user_id: str,
    amount: float,
    currency: str
) -> None:
    """
    Handle fallback logic for failed transfers.
    
    This attempts to recover from failures at different stages of the transfer process.
    
    Args:
        result: The current result dictionary with existing operation results
        user_id: User ID for the transfer
        amount: Amount being transferred
        currency: Currency being used
    """
    # Check where the failure occurred and apply appropriate fallback
    if result["debit"] and not result["mint"]:
        # Failed after debit but before mint - refund the user
        logger.info(f"Initiating refund for user {user_id} of {amount} {currency}")
        await send_fiat(user_id, amount, currency, refund=True)
        result["status"] = "refunded"
        
    elif result["mint"] and not result["redeem"]:
        # Failed after mint but before redemption
        # This is a complex state requiring manual intervention
        logger.critical(
            f"Transfer in indeterminate state. Minted but not redeemed. "
            f"Transaction ID: {result['mint'].tx_id}, Amount: {amount} {currency}"
        )
        result["status"] = "indeterminate_needs_review"
        
    elif result["redeem"] and not result["payout"]:
        # Failed after redemption but before payout
        # Need to retry the payout or notify operations team
        logger.error(
            f"Funds redeemed but payout failed. "
            f"Redemption ID: {result['redeem'].tx_id}, Amount: {amount} {currency}"
        )
        result["status"] = "redemption_complete_payout_failed"
        
    # Add additional logic for other failure scenarios if needed 