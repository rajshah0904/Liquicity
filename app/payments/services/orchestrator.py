"""
Payment orchestration service for TerraFlow.

This module provides high-level orchestration of payment flows,
coordinating between different payment providers and cross-chain bridge operations.
"""

import logging
from typing import Dict, Any, Optional

from .payment_service import receive_fiat, send_fiat
from ..providers.bridge_adapter import get_bridge_provider
from ..providers.factory import get_provider

logger = logging.getLogger(__name__)

async def transfer_cross_border(
    user_id: str,
    amount: float,
    src_cc: str,
    dst_cc: str,
    currency: str,
    src_chain: str = "1", # Ethereum Mainnet chain ID
    dst_chain: str = "137", # Polygon chain ID
    recipient: str = None,
    metadata: Optional[Dict[str, Any]] = None,
    dst_currency: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute a cross-border transfer using cross-chain bridges as an intermediary.
    
    This orchestrates a complete flow from source fiat currency to destination fiat currency,
    using Stargate Protocol as a bridge for the cross-border transfer.
    
    Flow:
    1. Pull funds from user's local payment source
    2. On-ramp via Stargate (unified liquidity pools across chains)
    3. Transfer across chains via Stargate (handled internally)
    4. Off-ramp to destination fiat
    5. Pay out to the recipient
    
    Args:
        user_id: ID of the user initiating the transfer
        amount: Amount to transfer
        src_cc: Source country code
        dst_cc: Destination country code
        currency: Currency to use (e.g., "USD")
        src_chain: Source blockchain chain ID (default: "1" for Ethereum)
        dst_chain: Destination blockchain chain ID (default: "137" for Polygon)
        recipient: Recipient wallet address on destination chain
        metadata: Optional additional data for the transaction
        dst_currency: Optional destination currency
        
    Returns:
        A dictionary with the results of each step
        
    Raises:
        ValueError: If any part of the transfer fails
    """
    result = {
        "debit": None,
        "bridge_onramp": None, 
        "bridge_offramp": None,
        "payout": None,
        "status": "pending",
        "errors": []
    }
    
    try:
        # Step 1: Pull local fiat from user's payment source
        logger.info(f"Initiating fiat debit for user {user_id}, amount {amount} {currency}")
        result["debit"] = await receive_fiat(user_id, amount, currency, country_code=src_cc)
        
        # Step 2: On-ramp via Stargate (unified liquidity pools across chains)
        logger.info(f"Bridging {amount} {currency} from chain {src_chain} to {dst_chain}")
        bridge = get_bridge_provider()
        result["bridge_onramp"] = await bridge.onramp(amount, currency, src_chain, dst_chain, recipient or user_id)
        
        # Step 3: Transfer across chains (handled internally by Stargate)
        logger.info(f"Cross-chain transfer complete with transaction ID: {result['bridge_onramp']['tx_id']}")
        
        # Step 4: Off-ramp to destination fiat
        logger.info(f"Off-ramping to fiat in destination country {dst_cc}")
        bank_account_id = metadata.get("bank_account_id") if metadata else None
        result["bridge_offramp"] = await bridge.offramp(amount, currency, dst_chain, bank_account_id or user_id)
        
        # Step 5: Pay out to the recipient
        logger.info(f"Sending fiat payout of {amount} {dst_currency or currency} to {dst_cc}")
        result["payout"] = await send_fiat(
            user_id=user_id, 
            amount=amount, 
            currency=dst_currency or currency, 
            country_code=dst_cc,
            metadata=metadata
        )
        
        result["status"] = "completed"
        return result
        
    except Exception as e:
        logger.error(f"Error during cross-border transfer: {str(e)}")
        result["status"] = "failed"
        result["errors"].append(str(e))
        
        # Attempt fallback and recovery based on where the failure occurred
        try:
            await _handle_transfer_fallback(result, user_id, amount, currency, src_cc)
        except Exception as fallback_error:
            logger.error(f"Fallback handling failed: {str(fallback_error)}")
            result["errors"].append(f"Fallback error: {str(fallback_error)}")
            
        return result

async def _handle_transfer_fallback(
    result: Dict[str, Any],
    user_id: str,
    amount: float,
    currency: str,
    country_code: str = "US"
) -> None:
    """
    Handle fallback logic for failed transfers.
    
    This attempts to recover from failures at different stages of the transfer process.
    
    Args:
        result: The current result dictionary with existing operation results
        user_id: User ID for the transfer
        amount: Amount being transferred
        currency: Currency being used
        country_code: Country code for refunds (default: US)
    """
    # Check where the failure occurred and apply appropriate fallback
    if result["debit"] and not result["bridge_onramp"]:
        # Failed after debit but before bridge on-ramp - refund the user
        logger.info(f"Initiating refund for user {user_id} of {amount} {currency}")
        await send_fiat(
            user_id=user_id, 
            amount=amount, 
            currency=currency, 
            country_code=country_code,
            refund=True
        )
        result["status"] = "refunded"
        
    elif result["bridge_onramp"] and not result["bridge_offramp"]:
        # Failed after on-ramp but before off-ramp
        # This is a complex state requiring manual intervention
        tx_id = result["bridge_onramp"].get("tx_id", "unknown") if isinstance(result["bridge_onramp"], dict) else getattr(result["bridge_onramp"], "tx_id", "unknown")
        logger.critical(
            f"Transfer in indeterminate state. On-ramped but not off-ramped. "
            f"Transaction ID: {tx_id}, Amount: {amount} {currency}"
        )
        result["status"] = "indeterminate_needs_review"
        
    elif result["bridge_offramp"] and not result["payout"]:
        # Failed after off-ramp but before payout
        # Need to retry the payout or notify operations team
        tx_id = result["bridge_offramp"].get("tx_id", "unknown") if isinstance(result["bridge_offramp"], dict) else getattr(result["bridge_offramp"], "tx_id", "unknown")
        logger.error(
            f"Funds off-ramped but payout failed. "
            f"Off-ramp ID: {tx_id}, Amount: {amount} {currency}"
        )
        result["status"] = "offramp_complete_payout_failed"
        
    # Add additional logic for other failure scenarios if needed 

async def transfer_domestic(
    user_id: str,
    amount: float,
    country_code: str,
    currency: str,
    preferred_rail: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute a domestic transfer within the same country.
    
    This optimized flow skips the blockchain bridge for same-country transfers,
    directly connecting the source and destination using the appropriate
    payment provider for the given country.
    
    Args:
        user_id: ID of the user initiating the transfer
        amount: Amount to transfer
        country_code: Country code for both source and destination
        currency: Currency to use (e.g., "USD")
        preferred_rail: Optional preferred payment rail/method
        metadata: Optional additional data for the transaction
        
    Returns:
        A dictionary with the results of the transfer
        
    Raises:
        ValueError: If the transfer fails
    """
    result = {
        "debit": None,
        "payout": None,
        "status": "pending",
        "errors": []
    }
    
    try:
        # Country code to uppercase
        country = country_code.upper()
        
        # Get the appropriate provider for this country
        provider = get_provider(country)
        
        # Prepare metadata
        transfer_metadata = {
            "user_id": user_id,
            "transfer_type": "domestic",
            "country": country,
        }
        
        if metadata:
            transfer_metadata.update(metadata)
        
        logger.info(f"Initiating domestic transfer for user {user_id}, amount {amount} {currency} in {country}")
        
        # Step 1: Pull funds from source account
        result["debit"] = await receive_fiat(user_id, amount, currency, country_code=country)
        
        logger.info(f"Debit completed with transaction ID: {result['debit'].transaction_id}")
        
        # Step 2: Pay out to destination account in the same country
        logger.info(f"Sending domestic payout of {amount} {currency} in {country}")
        result["payout"] = await send_fiat(
            user_id=user_id, 
            amount=amount, 
            currency=currency, 
            country_code=country,
            preferred_rail=preferred_rail,
            metadata=transfer_metadata
        )
        
        logger.info(f"Payout completed with transaction ID: {result['payout'].transaction_id}")
        
        result["status"] = "completed"
        return result
        
    except Exception as e:
        logger.error(f"Error during domestic transfer: {str(e)}")
        result["status"] = "failed"
        result["errors"].append(str(e))
        
        # Attempt fallback and recovery if debit succeeded but payout failed
        if result["debit"] and not result["payout"]:
            try:
                logger.info(f"Initiating refund for user {user_id} of {amount} {currency}")
                await send_fiat(
                    user_id=user_id, 
                    amount=amount, 
                    currency=currency, 
                    country_code=country,
                    refund=True
                )
                result["status"] = "refunded"
            except Exception as fallback_error:
                logger.error(f"Refund failed: {str(fallback_error)}")
                result["errors"].append(f"Refund error: {str(fallback_error)}")
                result["status"] = "debit_succeeded_payout_failed_refund_failed"
        
        return result 