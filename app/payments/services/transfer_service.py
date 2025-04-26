"""
Transfer service for TerraFlow.

This service provides a unified interface for all types of money transfers,
automatically selecting the optimal transfer method based on source and destination.
"""

import logging
from typing import Dict, Any, Optional
from .orchestrator import transfer_cross_border, transfer_domestic

logger = logging.getLogger(__name__)

async def transfer_money(
    user_id: str,
    amount: float,
    src_cc: str,
    dst_cc: str,
    currency: str,
    preferred_rail: Optional[str] = None,
    src_chain: str = "1",  # Ethereum Mainnet chain ID
    dst_chain: str = "137",  # Polygon chain ID
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Transfer money from one account to another, automatically selecting
    the optimal transfer method (domestic or cross-border) based on the
    source and destination countries.
    
    Args:
        user_id: ID of the user initiating the transfer
        amount: Amount to transfer
        src_cc: Source country code
        dst_cc: Destination country code
        currency: Currency to use (e.g., "USD")
        preferred_rail: Optional preferred payment rail/method (for domestic transfers)
        src_chain: Source blockchain chain ID (for cross-border transfers)
        dst_chain: Destination blockchain chain ID (for cross-border transfers)
        metadata: Optional additional data for the transaction
        
    Returns:
        A dictionary with the results of the transfer
    """
    # Normalize country codes
    src_country = src_cc.upper()
    dst_country = dst_cc.upper()
    
    # Determine appropriate source and destination currencies
    src_currency = currency
    dst_currency = currency
    
    # Source country currency validation
    if src_country == "US" and currency != "USD":
        src_currency = "USD"
        logger.info(f"Using USD for US source country (instead of {currency})")
    elif src_country == "CA" and currency != "CAD":
        src_currency = "CAD"
        logger.info(f"Using CAD for Canadian source country (instead of {currency})")
    elif src_country == "NG" and currency != "NGN":
        src_currency = "NGN"
        logger.info(f"Using NGN for Nigerian source country (instead of {currency})")
    
    # Destination country currency validation
    if dst_country == "US" and dst_currency != "USD":
        dst_currency = "USD"
        logger.info(f"Using USD for US destination (instead of {currency})")
    elif dst_country == "CA" and dst_currency != "CAD":
        dst_currency = "CAD"
        logger.info(f"Using CAD for Canadian destination (instead of {currency})")
    elif dst_country == "NG" and dst_currency != "NGN":
        dst_currency = "NGN"
        logger.info(f"Using NGN for Nigerian destination (instead of {currency})")
    
    # Add transfer info to metadata
    transfer_metadata = {
        "user_id": user_id,
        "source_country": src_country,
        "destination_country": dst_country,
    }
    
    if metadata:
        transfer_metadata.update(metadata)
    
    # Determine if this is a domestic or cross-border transfer
    if src_country == dst_country:
        logger.info(f"Initiating domestic transfer within {src_country}")
        return await transfer_domestic(
            user_id=user_id,
            amount=amount,
            country_code=src_country,
            currency=src_currency,
            preferred_rail=preferred_rail,
            metadata=transfer_metadata
        )
    else:
        logger.info(f"Initiating cross-border transfer from {src_country} to {dst_country}")
        return await transfer_cross_border(
            user_id=user_id,
            amount=amount,
            src_cc=src_country,
            dst_cc=dst_country,
            currency=src_currency,
            src_chain=src_chain,
            dst_chain=dst_chain,
            metadata=transfer_metadata,
            dst_currency=dst_currency
        ) 