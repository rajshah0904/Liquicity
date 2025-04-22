from typing import Dict, Optional, Type, Union, cast

from .modern_treasury import ModernTreasuryProvider
from .rapyd import RapydProvider
from .base import PaymentProvider
from .circle_provider import CircleProvider
from .stablecoin_base import StablecoinProvider

# Map of country codes to provider classes
COUNTRY_PROVIDER_MAP: Dict[str, Type[PaymentProvider]] = {
    "US": ModernTreasuryProvider,
    "CA": RapydProvider,
    "MX": RapydProvider,
    "NG": RapydProvider,
}

# Provider instances cache
_provider_instances: Dict[str, PaymentProvider] = {}
_stablecoin_provider_instance: Optional[StablecoinProvider] = None

def get_provider(country_code: str) -> PaymentProvider:
    """
    Get the appropriate payment provider for a country code.
    
    Args:
        country_code: ISO-2 country code (e.g., 'US', 'CA')
        
    Returns:
        An instance of the appropriate PaymentProvider
        
    Raises:
        ValueError: If no provider is available for the given country code
    """
    c = country_code.upper()
    
    # Check if the instance is already cached
    if c in _provider_instances:
        return _provider_instances[c]
    
    # Create a new instance if needed
    if c == "US":
        provider = ModernTreasuryProvider()
    elif c in ("CA", "MX", "NG"):
        provider = RapydProvider()
    else:
        raise ValueError(f"No payment provider available for country code: {country_code}")
    
    # Cache the instance for future use
    _provider_instances[c] = provider
    
    return provider 

def get_stablecoin_provider() -> StablecoinProvider:
    """
    Get the stablecoin provider instance.
    
    Returns:
        An instance of StablecoinProvider (currently only CircleProvider is supported)
    """
    global _stablecoin_provider_instance
    
    if _stablecoin_provider_instance is None:
        _stablecoin_provider_instance = CircleProvider()
        
    return _stablecoin_provider_instance 