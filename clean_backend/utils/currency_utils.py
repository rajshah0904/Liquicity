"""
Currency utility functions for mapping regions to their primary currencies.
"""

def get_fiat_currency_from_region(region: str) -> str:
    """
    Map user's selected region to primary fiat currency ISO code.
    
    Args:
        region: Region code (e.g., 'us', 'eu', 'mexico', 'brazil', etc.)
    
    Returns:
        3-letter currency code (e.g., 'USD', 'EUR', 'MXN', 'BRL', etc.)
    """
    # Region to currency mapping for supported regions only
    REGION_TO_CURRENCY = {
        'us': 'USD',        # United States
        'eu': 'EUR',        # European Union (SEPA)
        'mexico': 'MXN',    # Mexico
        'brazil': 'BRL',    # Brazil
        'colombia': 'COP',  # Colombia
        'peru': 'PEN',      # Peru
        'argentina': 'ARS', # Argentina
    }
    
    # Default to USD if region not found
    return REGION_TO_CURRENCY.get(region.lower() if region else '', 'USD')

def get_supported_regions():
    """
    Get list of supported regions for region selection.
    
    Returns:
        List of tuples (region_code, display_name, currency)
    """
    return [
        ('us', 'United States', 'USD'),
        ('eu', 'European Union', 'EUR'),
        ('mexico', 'Mexico', 'MXN'),
        ('brazil', 'Brazil', 'BRL'),
        ('colombia', 'Colombia', 'COP'),
        ('peru', 'Peru', 'PEN'),
        ('argentina', 'Argentina', 'ARS'),
    ] 