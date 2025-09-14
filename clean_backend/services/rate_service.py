"""
Rate Service for fetching exchange rates from Bridge API
- Bridge only supports reliable USD -> FIAT quotes
- For FIAT -> USD/USDC, we invert the USD -> FIAT quote
- USDC is 1:1 with USD, so USDC/FIAT = USD/FIAT (inverted from USD->FIAT)
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
        self.api_key = settings.bridge_api_key  # plain string
        self.timeout = 30
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Api-Key": self.api_key,
            "accept": "application/json",
            "Content-Type": "application/json",
        }
    
    def _usd_to(self, to_currency: str) -> Optional[Decimal]:
        """Fetch Bridge USD->to_currency midmarket rate."""
        to_currency = to_currency.lower()
        try:
            url = f"{self.base_url}/exchange_rates"
            params = {"from": "usd", "to": to_currency}
            resp = requests.get(url, headers=self._get_headers(), params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            mid = data.get("midmarket_rate") or data.get("rate") or data.get("exchange_rate")
            if mid is None:
                logger.error(f"No midmarket_rate in USD->{to_currency} response: {data}")
                return None
            return Decimal(str(mid))
        except requests.RequestException as e:
            logger.error(f"Bridge rate fetch failed USD->{to_currency}: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Invalid USD->{to_currency} response: {e}")
            return None
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """
        General FX rate using Bridge USD legs:
        - If same currency → 1.0
        - If from=usd → USD->to via Bridge
        - If to=usd → invert USD->from
        - Else cross via USD: (USD->to) / (USD->from)
        Returns Decimal or None on failure.
        """
        f = from_currency.lower()
        t = to_currency.lower()
        if f == t:
            return Decimal("1.0")
        if f == "usd":
            return self._usd_to(t)
        if t == "usd":
            base = self._usd_to(f)
            if base is None or base == 0:
                return None
            return Decimal("1") / base
        # Cross via USD
        usd_to_f = self._usd_to(f)
        usd_to_t = self._usd_to(t)
        if usd_to_f is None or usd_to_f == 0 or usd_to_t is None:
            return None
        # 1 f = (usd_to_t / usd_to_f) t
        return (usd_to_t / usd_to_f)

    def get_usdc_rate(self, currency: str) -> Optional[Decimal]:
        """
        Return USDC per 1 unit of `currency` (USDC/FIAT).
        - USDC/FIAT = USD/FIAT = 1 / (USD->FIAT midmarket)
        - For USD, return 1.0
        """
        c = currency.lower()
        if c == "usd":
            return Decimal("1.0")
        usd_to_c = self._usd_to(c)
        if usd_to_c is None or usd_to_c == 0:
            return None
        return Decimal("1") / usd_to_c
    
    def convert_to_usdc(self, amount: Decimal, from_currency: str) -> Optional[Decimal]:
        rate = self.get_usdc_rate(from_currency)
        if rate is None:
            return None
        return amount * rate
    
    def convert_from_usdc(self, usdc_amount: Decimal, to_currency: str) -> Optional[Decimal]:
        rate = self.get_usdc_rate(to_currency)
        if rate is None or rate == 0:
            return None
        return usdc_amount / rate

# Global rate service instance
rate_service = RateService() 