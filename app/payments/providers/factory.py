from typing import Dict, Optional, Type, Union, cast

from .modern_treasury import ModernTreasuryProvider
from .rapyd import RapydProvider
from .base import PaymentProvider

# Map of country codes to provider classes
COUNTRY_PROVIDER_MAP: Dict[str, Type[PaymentProvider]] = {
    "US": ModernTreasuryProvider,
    "CA": RapydProvider,
    "MX": RapydProvider,
    "NG": RapydProvider,
}

# Provider instances cache
_provider_instances: Dict[str, PaymentProvider] = {}

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
    provider_class = None
    
    if c == "US":
        provider_class = ModernTreasuryProvider
    elif c in ("CA", "MX", "NG"):
        provider_class = RapydProvider
    else:
        raise ValueError(f"No payment provider available for country code: {country_code}")
    
    # Check if we already have an instance of this provider class
    for instance in _provider_instances.values():
        if isinstance(instance, provider_class):
            # Cache this instance for the current country code too
            _provider_instances[c] = instance
            return instance
    
    # Create new instance if we don't have one
    provider = provider_class()
    
    # Cache the instance for future use
    _provider_instances[c] = provider
    
    return provider

# Note: Bridge provider functionality has been moved to TypeScript
# and is available in factory.ts as getBridgeProvider() 