import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode
import json
from typing import Dict, List, Optional, Union, Any
import os
from app.config import config

class BinanceAPI:
    """
    Binance API wrapper for TerraFlow
    Provides functionality for market data and trading operations
    """
    
    def __init__(self, testnet: bool = False):
        self.api_key = os.getenv("BINANCE_API_KEY", "")
        self.api_secret = os.getenv("BINANCE_API_SECRET", "")
        
        # Use testnet or production endpoints
        if testnet:
            self.base_url = "https://testnet.binance.vision/api"
            self.base_wapi_url = "https://testnet.binance.vision/wapi"
        else:
            self.base_url = "https://api.binance.com/api"
            self.base_wapi_url = "https://api.binance.com/wapi"
    
    def _get_signature(self, params: Dict[str, Any]) -> str:
        """Generate HMAC SHA256 signature for authenticated endpoints"""
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with API key for authenticated requests"""
        return {
            'X-MBX-APIKEY': self.api_key
        }
    
    def get_ticker_price(self, symbol: str) -> Optional[float]:
        """
        Get latest price for a symbol
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            The current price as a float
        """
        try:
            endpoint = f"{self.base_url}/v3/ticker/price"
            params = {'symbol': symbol}
            response = requests.get(endpoint, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return float(data.get('price', 0))
            return None
        except Exception as e:
            print(f"Error fetching ticker price for {symbol}: {str(e)}")
            return None
    
    def get_exchange_info(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get exchange trading rules and symbol information
        
        Args:
            symbol: Optional specific trading pair to query
            
        Returns:
            Exchange information
        """
        try:
            endpoint = f"{self.base_url}/v3/exchangeInfo"
            params = {}
            if symbol:
                params['symbol'] = symbol
                
            response = requests.get(endpoint, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"Error fetching exchange info: {str(e)}")
            return {}
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information including balances
        Requires API key with appropriate permissions
        
        Returns:
            Account information and balances
        """
        try:
            endpoint = f"{self.base_url}/v3/account"
            timestamp = int(time.time() * 1000)
            params = {'timestamp': timestamp}
            
            # Add signature
            signature = self._get_signature(params)
            params['signature'] = signature
            
            response = requests.get(
                endpoint, 
                params=params, 
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            
            print(f"Error getting account info: {response.status_code}, {response.text}")
            return {}
        except Exception as e:
            print(f"Exception getting account info: {str(e)}")
            return {}
    
    def place_order(
        self, 
        symbol: str, 
        side: str, 
        order_type: str, 
        quantity: float,
        price: Optional[float] = None,
        time_in_force: str = "GTC",
        new_client_order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Place a new order
        
        Args:
            symbol: Trading pair
            side: 'BUY' or 'SELL'
            order_type: 'LIMIT', 'MARKET', etc.
            quantity: Order size
            price: Required for limit orders
            time_in_force: 'GTC', 'IOC', 'FOK'
            new_client_order_id: Optional client order ID
            
        Returns:
            Order response
        """
        try:
            endpoint = f"{self.base_url}/v3/order"
            timestamp = int(time.time() * 1000)
            
            # Build params
            params = {
                'symbol': symbol,
                'side': side.upper(),
                'type': order_type.upper(),
                'quantity': quantity,
                'timestamp': timestamp
            }
            
            # Add optional params
            if price and order_type.upper() == 'LIMIT':
                params['price'] = price
                params['timeInForce'] = time_in_force
                
            if new_client_order_id:
                params['newClientOrderId'] = new_client_order_id
                
            # Add signature
            signature = self._get_signature(params)
            params['signature'] = signature
            
            # Send request
            response = requests.post(
                endpoint, 
                params=params, 
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
                
            print(f"Error placing order: {response.status_code}, {response.text}")
            return {'error': response.text}
        except Exception as e:
            print(f"Exception placing order: {str(e)}")
            return {'error': str(e)}
    
    def get_stablecoin_conversion_rate(
        self, 
        from_currency: str, 
        to_currency: str
    ) -> Optional[float]:
        """
        Get conversion rate between currencies or stablecoins
        
        Args:
            from_currency: Source currency (e.g., 'USD', 'USDT')
            to_currency: Target currency (e.g., 'EUR', 'USDC')
            
        Returns:
            Conversion rate or None if unavailable
        """
        # Normalize inputs
        from_curr = from_currency.upper()
        to_curr = to_currency.upper()
        
        # If same currency, rate is 1:1
        if from_curr == to_curr:
            return 1.0
            
        try:
            # For stablecoin to stablecoin (e.g., USDT/USDC)
            if from_curr in ['USDT', 'USDC', 'BUSD', 'DAI'] and to_curr in ['USDT', 'USDC', 'BUSD', 'DAI']:
                # Try direct pair first
                symbol = f"{from_curr}{to_curr}"
                price = self.get_ticker_price(symbol)
                
                if price:
                    return price
                    
                # Try reverse pair
                symbol = f"{to_curr}{from_curr}"
                price = self.get_ticker_price(symbol)
                
                if price:
                    return 1.0 / price
                    
                # If no direct pair exists, use BTC as intermediary
                # from_curr → BTC → to_curr
                symbol1 = f"{from_curr}BTC"
                price1 = self.get_ticker_price(symbol1)
                
                symbol2 = f"{to_curr}BTC"
                price2 = self.get_ticker_price(symbol2)
                
                if price1 and price2:
                    return price1 / price2
            
            # For fiat to stablecoin or stablecoin to fiat
            # This is approximate - in production, use proper forex data
            # and stablecoin market rates
            
            # Rough mapping of fiat to stablecoin
            stablecoin_map = {
                'USD': 'USDT',
                'EUR': 'EURT',
                'GBP': 'GBPT',
                'AUD': 'AUDT'
            }
            
            if from_curr in stablecoin_map.keys() and to_curr in ['USDT', 'USDC', 'BUSD', 'DAI']:
                # Fiat to stablecoin
                fiat_stablecoin = stablecoin_map.get(from_curr, 'USDT')
                
                if fiat_stablecoin == to_curr:
                    return 1.0
                
                # Get rate from mapped stablecoin to target stablecoin
                return self.get_stablecoin_conversion_rate(fiat_stablecoin, to_curr)
                
            if from_curr in ['USDT', 'USDC', 'BUSD', 'DAI'] and to_curr in stablecoin_map.keys():
                # Stablecoin to fiat
                fiat_stablecoin = stablecoin_map.get(to_curr, 'USDT')
                
                if from_curr == fiat_stablecoin:
                    return 1.0
                
                # Get rate from source stablecoin to mapped stablecoin
                return self.get_stablecoin_conversion_rate(from_curr, fiat_stablecoin)
            
            # If all else fails, return None to indicate conversion not possible
            return None
            
        except Exception as e:
            print(f"Error getting conversion rate {from_curr}/{to_curr}: {str(e)}")
            return None
            
    def get_balances(self) -> Dict[str, float]:
        """
        Get account balances for all assets
        
        Returns:
            Dictionary of asset -> free balance
        """
        account_info = self.get_account_info()
        
        if not account_info or 'balances' not in account_info:
            return {}
            
        balances = {}
        for asset_data in account_info['balances']:
            asset = asset_data.get('asset', '')
            free = float(asset_data.get('free', 0))
            
            if free > 0:
                balances[asset] = free
                
        return balances

# Create global instance for convenience
binance_client = BinanceAPI(testnet=config.environment != "production")

def get_binance_client() -> BinanceAPI:
    """Get the Binance API client instance"""
    return binance_client 