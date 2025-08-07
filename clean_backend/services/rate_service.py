"""
Rate Service for fetching exchange rates from Bridge API
Uses midmarket_rate from Bridge's /v0/exchange_rates endpoint
"""

import requests
from decimal import Decimal
from typing import Dict, Optional
from ..config.settings import settings
import logging

logger = logging.getLogger(__name__)

class RateService:
    """Service for fetching exchange rates from Bridge API"""
    
    def __init__(self):
        self.base_url = settings.bridge_base_url
        self.api_key = settings.bridge_api_key.get_secret_value()
        self.timeout = settings.bridge_timeout
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Bridge API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """
        Get midmarket exchange rate between two currencies from Bridge API
        
        Args:
            from_currency: Source currency code (e.g. 'usd', 'eur', 'mxn')
            to_currency: Target currency code (e.g. 'usd', 'eur', 'mxn')
            
        Returns:
            Decimal: The midmarket exchange rate, or None if not available
            
        Supported pairs as of December 2024:
        - USD <-> EUR
        - USD <-> MXN  
        - BTC -> USD
        - ETH -> USD
        - SOL -> USD
        """
        
        # Normalize currency codes to lowercase
        from_currency = from_currency.lower()
        to_currency = to_currency.lower()
        
        # If same currency, rate is 1
        if from_currency == to_currency:
            return Decimal('1.0')
            
        try:
            url = f"{self.base_url}/exchange_rates"
            params = {
                'from': from_currency,
                'to': to_currency
            }
            
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Use midmarket_rate as specified
            midmarket_rate = data.get('midmarket_rate')
            if midmarket_rate is None:
                logger.error(f"No midmarket_rate in response for {from_currency}->{to_currency}: {data}")
                return None
                
            return Decimal(str(midmarket_rate))
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch exchange rate {from_currency}->{to_currency}: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Invalid exchange rate response for {from_currency}->{to_currency}: {e}")
            return None
    
    def get_usdc_rate(self, currency: str) -> Optional[Decimal]:
        """
        Get exchange rate from currency to USDC
        Since USDC is pegged 1:1 to USD, this gets currency->USD rate
        
        Args:
            currency: Currency code (e.g. 'eur', 'mxn')
            
        Returns:
            Decimal: Exchange rate to USDC, or None if not available
        """
        currency = currency.lower()
        
        # USDC is 1:1 pegged to USD
        if currency == 'usd':
            return Decimal('1.0')
            
        # For other currencies, get rate to USD (which equals rate to USDC)
        return self.get_exchange_rate(currency, 'usd')
    
    def convert_to_usdc(self, amount: Decimal, from_currency: str) -> Optional[Decimal]:
        """
        Convert amount from currency to USDC equivalent
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            
        Returns:
            Decimal: USDC equivalent amount, or None if conversion fails
        """
        rate = self.get_usdc_rate(from_currency)
        if rate is None:
            return None
            
        return amount * rate
    
    def convert_from_usdc(self, usdc_amount: Decimal, to_currency: str) -> Optional[Decimal]:
        """
        Convert USDC amount to target currency
        
        Args:
            usdc_amount: USDC amount to convert
            to_currency: Target currency code
            
        Returns:
            Decimal: Amount in target currency, or None if conversion fails
        """
        rate = self.get_usdc_rate(to_currency)
        if rate is None:
            return None
            
        # Convert USDC to target currency (divide by USD rate)
        return usdc_amount / rate

# Global rate service instance
rate_service = RateService() 