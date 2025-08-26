"""
VelaFi API Client for LATAM KYC Integration

VelaFi processing times for LATAM:
- Initial submission: Instant
- Document review: 2-3 business days
- Final approval: Up to 5 business days for complex cases

Supported countries: Mexico, Brazil, Colombia, Peru, Argentina
Languages: Spanish (es), Portuguese (pt), English (en)
"""

import requests
import logging
import os
from typing import Dict, Optional, Any

_log = logging.getLogger(__name__)

class VelaFiClient:
    def __init__(self):
        self.base_url = os.getenv("VELAFI_API_URL", "https://api.velafi.com/v1")
        self.api_key = os.getenv("VELAFI_API_KEY")
        self.webhook_secret = os.getenv("VELAFI_WEBHOOK_SECRET")
        
        if not self.api_key:
            _log.warning("VelaFi API key not configured - VelaFi features will be disabled")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to VelaFi API"""
        if not self.api_key:
            raise Exception("VelaFi API key not configured")
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.request(method, url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            _log.error(f"VelaFi API request failed: {e}")
            raise Exception(f"VelaFi API error: {e}")
    
    def create_merchant(self, payload: Dict) -> Dict:
        """
        Create VelaFi INDIVIDUAL merchant for KYC
        
        Args:
            payload: {
                "merchantName": "User's full legal name",
                "email": "user@example.com", 
                "merchantType": "INDIVIDUAL",
                "callbackUrl": "https://app.example.com/api/kyc/velafi/callback",
                "languageCode": "es|pt|en"  # Based on country
            }
        
        Returns:
            {
                "merchantId": "string",
                "kycLink": "https://kyc.velafi.com/...",
                "status": "pending",
                "estimatedProcessingTime": "2-3 business days"
            }
        """
        _log.info(f"Creating VelaFi merchant for: {payload.get('email')}")
        
        # Add processing time estimate to response
        result = self._make_request("POST", "/merchants", payload)
        result["estimatedProcessingTime"] = "2-3 business days"
        result["maxProcessingTime"] = "5 business days for complex cases"
        
        return result
    
    def get_merchant_status(self, merchant_id: str) -> Dict:
        """
        Get VelaFi merchant KYC status
        
        Returns:
            {
                "merchantId": "string",
                "status": "pending|approved|rejected|under_review",
                "kycLink": "https://...",
                "rejectionReason": "string|null",
                "completedAt": "ISO date|null",
                "documents": [...],
                "processingDays": 2
            }
        """
        _log.info(f"Checking VelaFi merchant status: {merchant_id}")
        return self._make_request("GET", f"/merchants/{merchant_id}/status")
    
    def verify_webhook(self, payload: str, signature: str) -> bool:
        """Verify VelaFi webhook signature"""
        # Implement signature verification based on VelaFi's webhook security
        # This is a placeholder - actual implementation depends on VelaFi's spec
        return True
    
    def get_language_code(self, country_code: str) -> str:
        """Get appropriate language code for VelaFi based on country"""
        language_mapping = {
            "MX": "es",  # Mexico - Spanish
            "BR": "pt",  # Brazil - Portuguese  
            "CO": "es",  # Colombia - Spanish
            "PE": "es",  # Peru - Spanish
            "AR": "es",  # Argentina - Spanish
        }
        return language_mapping.get(country_code.upper(), "en")
    
    def get_processing_estimate(self, country_code: str) -> Dict:
        """Get processing time estimates for specific country"""
        base_estimate = {
            "typical": "2-3 business days",
            "maximum": "5 business days",
            "initial_review": "24 hours",
            "document_verification": "1-2 business days",
            "final_approval": "1-2 business days"
        }
        
        # Country-specific adjustments
        if country_code.upper() == "BR":
            base_estimate["typical"] = "3-4 business days"  # Brazil has additional compliance
            base_estimate["document_verification"] = "2-3 business days"
        
        return base_estimate

# Singleton instance
velafi_client = VelaFiClient()