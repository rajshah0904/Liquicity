"""
KYC region mappings and configurations for international flow
Mirrors US implementation patterns exactly
"""

from typing import Dict, List, Set
from enum import Enum

class Region(str, Enum):
    US = "us"
    EU = "eu"
    MEXICO = "mexico"
    BRAZIL = "brazil"
    COLOMBIA = "colombia"
    PERU = "peru"
    ARGENTINA = "argentina"

# LATAM countries (now using Bridge only)
LATAM_COUNTRIES: Set[str] = {
    "MX",  # Mexico
    "BR",  # Brazil
    "CO",  # Colombia
    "PE",  # Peru
    "AR",  # Argentina
}

# EU countries (major SEPA countries for now)
EU_COUNTRIES: Set[str] = {
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", 
    "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", 
    "PL", "PT", "RO", "SK", "SI", "ES", "SE", "IS", "LI", "NO"
}

# Bridge endorsement mappings (env-configurable for non-sepa)
BRIDGE_ENDORSEMENTS: Dict[str, List[str]] = {
    # EU uses SEPA
    **{country: ["sepa"] for country in EU_COUNTRIES},
    
    # LATAM specific endorsements
    "MX": ["spei"],
    "BR": ["pix"],
    "CO": ["local_transfer_co"],
    "PE": ["local_transfer_pe"],
    "AR": ["local_transfer_ar"],
    
    # US (reference)
    "US": ["ach"],
}

# Region display names
REGION_DISPLAY_NAMES: Dict[Region, str] = {
    Region.US: "United States",
    Region.EU: "European Union",
    Region.MEXICO: "Mexico",
    Region.BRAZIL: "Brazil",
    Region.COLOMBIA: "Colombia",
    Region.PERU: "Peru",
    Region.ARGENTINA: "Argentina",
}

# Countries to show in region selector (based on spec)
AVAILABLE_COUNTRIES = [
    # EU (show as one option)
    {"code": "EU", "name": "European Union", "region": Region.EU},
    
    # Individual LATAM countries
    {"code": "MX", "name": "Mexico", "region": Region.MEXICO},
    {"code": "BR", "name": "Brazil", "region": Region.BRAZIL},
    {"code": "CO", "name": "Colombia", "region": Region.COLOMBIA},
    {"code": "PE", "name": "Peru", "region": Region.PERU},
    {"code": "AR", "name": "Argentina", "region": Region.ARGENTINA},
    
    # US (keep as reference)
    {"code": "US", "name": "United States", "region": Region.US},
]

def get_region_for_country(country_code: str) -> Region:
    """Get region for country code"""
    country_code = country_code.upper()
    
    if country_code in EU_COUNTRIES or country_code == "EU":
        return Region.EU
    elif country_code == "MX":
        return Region.MEXICO
    elif country_code == "BR":
        return Region.BRAZIL
    elif country_code == "CO":
        return Region.COLOMBIA
    elif country_code == "PE":
        return Region.PERU
    elif country_code == "AR":
        return Region.ARGENTINA
    elif country_code == "US":
        return Region.US
    else:
        return Region.US  # Default fallback



def get_bridge_endorsements(country_code: str) -> List[str]:
    """Get Bridge endorsements for country"""
    country_code = country_code.upper()
    return BRIDGE_ENDORSEMENTS.get(country_code, ["wire"])



def get_form_config_for_region(region: Region) -> Dict:
    """Get form configuration for region"""
    configs = {
        Region.EU: {
            "national_id_label": "National ID",
            "national_id_hint": "Government-issued ID number",
            "bank_field_hint": "IBAN",
            "address_country_required": True,
            "address_country_must_be_eu": True,
        },
        Region.MEXICO: {
            "national_id_label": "National ID",
            "national_id_hint": "CURP/RFC as applicable",
            "bank_field_hint": "CLABE",
            "address_country_required": True,
            "address_country_must_be": ["MX"],
        },
        Region.BRAZIL: {
            "national_id_label": "National ID",
            "national_id_hint": "CPF",
            "bank_field_hint": "PIX key",
            "address_country_required": True,
            "address_country_must_be": ["BR"],
        },
        Region.COLOMBIA: {
            "national_id_label": "National ID",
            "national_id_hint": "Cédula (CC/NIT)",
            "bank_field_hint": "",
            "address_country_required": True,
            "address_country_must_be": ["CO"],
        },
        Region.PERU: {
            "national_id_label": "National ID",
            "national_id_hint": "DNI/CE",
            "bank_field_hint": "",
            "address_country_required": True,
            "address_country_must_be": ["PE"],
        },
        Region.ARGENTINA: {
            "national_id_label": "National ID",
            "national_id_hint": "DNI",
            "bank_field_hint": "CBU/alias",
            "address_country_required": True,
            "address_country_must_be": ["AR"],
        },
        Region.US: {
            "national_id_label": "SSN",
            "national_id_hint": "Social Security Number",
            "bank_field_hint": "Routing/Account",
            "address_country_required": True,
            "address_country_must_be": ["US"],
        },
    }
    
    return configs.get(region, configs[Region.US])