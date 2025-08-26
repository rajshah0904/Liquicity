"""
Bridge Customer Service - Handles region-specific customer creation
"""
import uuid
from typing import Dict, Any, Optional
from ..bridge import BridgeClient
import logging

_log = logging.getLogger(__name__)


class BridgeCustomerService:
    """Service for creating Bridge customers with region-specific payloads"""
    
    def __init__(self):
        self.client = BridgeClient()
    
    def create_customer_for_region(
        self, 
        region: str, 
        user_data: Dict[str, Any], 
        signed_agreement_id: str
    ) -> Dict[str, Any]:
        """
        Create a Bridge customer with region-specific payload structure
        
        Args:
            region: Region code ('us', 'international', 'europe')
            user_data: User data from frontend form
            signed_agreement_id: Bridge signed agreement ID
            
        Returns:
            Bridge customer creation response
        """
        
        # Base payload structure
        base_payload = {
            "type": "individual",
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "email": user_data.get("email"),
            "birth_date": user_data.get("birth_date"),
            "signed_agreement_id": signed_agreement_id,
            "residential_address": {
                "street_line_1": user_data.get("street_line_1"),
                "city": user_data.get("city"),
                "subdivision": user_data.get("subdivision"),
                "postal_code": user_data.get("postal_code"),
                "country": user_data.get("country")
            }
        }
        
        # Add street_line_2 if provided
        if user_data.get("street_line_2"):
            base_payload["residential_address"]["street_line_2"] = user_data.get("street_line_2")
        
        # Region-specific customizations
        if region.lower() == "us":
            payload = self._create_us_payload(base_payload, user_data)
        elif region.lower() == "international":
            payload = self._create_international_payload(base_payload, user_data)
        elif region.lower() == "europe":
            payload = self._create_europe_payload(base_payload, user_data)
        else:
            # Default to international for unknown regions
            _log.warning(f"Unknown region '{region}', defaulting to international payload")
            payload = self._create_international_payload(base_payload, user_data)
        
        # Create customer via Bridge API
        _log.info(f"Creating Bridge customer for region: {region}")
        return self.client.create_customer(payload)
    
    def _create_us_payload(self, base_payload: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create US-specific payload"""
        payload = base_payload.copy()
        
        # US requires SSN and drivers license or passport
        identifying_info = []
        
        # Add SSN
        if user_data.get("ssn"):
            identifying_info.append({
                "type": "ssn",
                "issuing_country": "usa",
                "number": user_data.get("ssn")
            })
        
        # Add ID document
        id_type = user_data.get("id_type", "drivers_license")
        if id_type == "drivers_license":
            id_info = {
                "type": "drivers_license",
                "issuing_country": "usa",
                "number": user_data.get("id_number")
            }
            if user_data.get("id_image_front"):
                id_info["image_front"] = user_data.get("id_image_front")
            if user_data.get("id_image_back"):
                id_info["image_back"] = user_data.get("id_image_back")
            identifying_info.append(id_info)
        else:
            # Passport or other ID
            id_info = {
                "type": id_type,
                "issuing_country": "usa",
                "number": user_data.get("id_number")
            }
            if user_data.get("id_image_front"):
                id_info["image_front"] = user_data.get("id_image_front")
            identifying_info.append(id_info)
        
        payload["identifying_information"] = identifying_info
        return payload
    
    def _create_international_payload(self, base_payload: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create International-specific payload (e.g., Argentina)"""
        payload = base_payload.copy()
        
        # Add phone if provided
        if user_data.get("phone"):
            payload["phone"] = user_data.get("phone")
        
        # Update address format for international
        address = payload["residential_address"]
        if user_data.get("state"):
            address["state"] = user_data.get("state")  # ISO 3166-2 subdivision code
        
        # Add additional required fields for international
        if user_data.get("employment_status"):
            payload["employment_status"] = user_data.get("employment_status")
        if user_data.get("expected_monthly_payments"):
            payload["expected_monthly_payments"] = user_data.get("expected_monthly_payments")
        if user_data.get("acting_as_intermediary"):
            payload["acting_as_intermediary"] = user_data.get("acting_as_intermediary")
        if user_data.get("most_recent_occupation"):
            payload["most_recent_occupation"] = user_data.get("most_recent_occupation")
        if user_data.get("account_purpose"):
            payload["account_purpose"] = user_data.get("account_purpose")
        if user_data.get("account_purpose_other"):
            payload["account_purpose_other"] = user_data.get("account_purpose_other")
        if user_data.get("source_of_funds"):
            payload["source_of_funds"] = user_data.get("source_of_funds")
        
        # Add identifying information (passport for international)
        identifying_info = []
        id_info = {
            "type": "passport",
            "issuing_country": user_data.get("country", "arg").lower(),
            "number": user_data.get("id_number")
        }
        if user_data.get("id_image_front"):
            id_info["image_front"] = user_data.get("id_image_front")
        if user_data.get("id_image_back"):
            id_info["image_back"] = user_data.get("id_image_back")
        identifying_info.append(id_info)
        
        payload["identifying_information"] = identifying_info
        return payload
    
    def _create_europe_payload(self, base_payload: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Europe-specific payload (e.g., UK)"""
        payload = base_payload.copy()
        
        # Add identifying information (passport for Europe)
        identifying_info = []
        id_info = {
            "type": "passport",
            "issuing_country": user_data.get("country", "gbr").lower(),
            "number": user_data.get("id_number")
        }
        if user_data.get("id_image_front"):
            id_info["image_front"] = user_data.get("id_image_front")
        identifying_info.append(id_info)
        
        payload["identifying_information"] = identifying_info
        
        # Add documents for proof of address
        if user_data.get("proof_of_address"):
            payload["documents"] = [{
                "purposes": ["proof_of_address"],
                "file": user_data.get("proof_of_address")
            }]
        
        return payload


# Global instance
bridge_customer_service = BridgeCustomerService()