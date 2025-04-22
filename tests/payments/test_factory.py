import pytest
from unittest.mock import patch, MagicMock

from app.payments.providers.factory import (
    get_provider, 
    get_stablecoin_provider,
    _provider_instances,
    _stablecoin_provider_instance
)
from app.payments.providers.modern_treasury import ModernTreasuryProvider
from app.payments.providers.rapyd import RapydProvider
from app.payments.providers.circle_provider import CircleProvider

@pytest.fixture(autouse=True)
def reset_caches():
    """Reset the cached instances before each test"""
    _provider_instances.clear()
    global _stablecoin_provider_instance
    _stablecoin_provider_instance = None

@pytest.mark.asyncio
async def test_get_provider_us():
    """Test that get_provider returns a ModernTreasuryProvider for US"""
    with patch('app.payments.providers.modern_treasury.os') as mock_os:
        mock_os.getenv.return_value = "test_api_key"
        
        provider = get_provider("US")
        
        assert isinstance(provider, ModernTreasuryProvider)
        assert "US" in _provider_instances
        assert _provider_instances["US"] is provider

@pytest.mark.asyncio
async def test_get_provider_ca():
    """Test that get_provider returns a RapydProvider for CA"""
    with patch('app.payments.providers.rapyd.os') as mock_os:
        mock_os.getenv.side_effect = lambda x: {
            "RAPYD_ACCESS_KEY": "test_access_key",
            "RAPYD_SECRET_KEY": "test_secret_key",
        }.get(x)
        
        provider = get_provider("CA")
        
        assert isinstance(provider, RapydProvider)
        assert "CA" in _provider_instances
        assert _provider_instances["CA"] is provider

@pytest.mark.asyncio
async def test_get_provider_mx():
    """Test that get_provider returns a RapydProvider for MX"""
    with patch('app.payments.providers.rapyd.os') as mock_os:
        mock_os.getenv.side_effect = lambda x: {
            "RAPYD_ACCESS_KEY": "test_access_key",
            "RAPYD_SECRET_KEY": "test_secret_key",
        }.get(x)
        
        provider = get_provider("MX")
        
        assert isinstance(provider, RapydProvider)
        assert "MX" in _provider_instances
        assert _provider_instances["MX"] is provider

@pytest.mark.asyncio
async def test_get_provider_invalid_country():
    """Test that get_provider raises an error for unsupported country codes"""
    with pytest.raises(ValueError, match="No payment provider available for country code"):
        get_provider("XYZ")

@pytest.mark.asyncio
async def test_get_provider_case_insensitive():
    """Test that get_provider is case-insensitive for country codes"""
    with patch('app.payments.providers.modern_treasury.os') as mock_os:
        mock_os.getenv.return_value = "test_api_key"
        
        provider_upper = get_provider("US")
        assert isinstance(provider_upper, ModernTreasuryProvider)
        
        # Should return the same cached instance
        provider_lower = get_provider("us")
        assert provider_lower is provider_upper

@pytest.mark.asyncio
async def test_get_provider_caching():
    """Test that providers are properly cached"""
    with patch('app.payments.providers.modern_treasury.os') as mock_os:
        mock_os.getenv.return_value = "test_api_key"
        
        # First call should create a new instance
        provider1 = get_provider("US")
        assert isinstance(provider1, ModernTreasuryProvider)
        
        # Second call should return the cached instance
        provider2 = get_provider("US")
        assert provider2 is provider1
        
        # ModernTreasuryProvider constructor should only be called once
        assert len(_provider_instances) == 1

@pytest.mark.asyncio
async def test_get_stablecoin_provider():
    """Test that get_stablecoin_provider returns a CircleProvider"""
    with patch('app.payments.providers.circle_provider.os') as mock_os:
        mock_os.getenv.return_value = "test_api_key"
        
        provider = get_stablecoin_provider()
        
        assert isinstance(provider, CircleProvider)
        assert _stablecoin_provider_instance is not None
        assert _stablecoin_provider_instance is provider

@pytest.mark.asyncio
async def test_get_stablecoin_provider_caching():
    """Test that stablecoin provider is properly cached"""
    with patch('app.payments.providers.circle_provider.os') as mock_os:
        mock_os.getenv.return_value = "test_api_key"
        
        # First call should create a new instance
        provider1 = get_stablecoin_provider()
        assert isinstance(provider1, CircleProvider)
        
        # Patch the CircleProvider constructor to verify it's not called again
        with patch('app.payments.providers.factory.CircleProvider') as mock_circle:
            # Second call should return the cached instance
            provider2 = get_stablecoin_provider()
            assert provider2 is provider1
            
            # CircleProvider constructor should not be called again
            mock_circle.assert_not_called()

@pytest.mark.asyncio
async def test_multiple_country_providers():
    """Test getting providers for multiple countries"""
    with patch('app.payments.providers.modern_treasury.os') as mt_mock_os, \
         patch('app.payments.providers.rapyd.os') as rapyd_mock_os:
        
        mt_mock_os.getenv.return_value = "test_mt_api_key"
        rapyd_mock_os.getenv.side_effect = lambda x: {
            "RAPYD_ACCESS_KEY": "test_access_key",
            "RAPYD_SECRET_KEY": "test_secret_key",
        }.get(x)
        
        # Get providers for different countries
        us_provider = get_provider("US")
        ca_provider = get_provider("CA")
        ng_provider = get_provider("NG")
        
        # Verify correct provider types
        assert isinstance(us_provider, ModernTreasuryProvider)
        assert isinstance(ca_provider, RapydProvider)
        assert isinstance(ng_provider, RapydProvider)
        
        # US provider should be different from CA/NG providers
        assert us_provider is not ca_provider
        assert us_provider is not ng_provider
        
        # CA and NG providers should be the same RapydProvider instance
        assert ca_provider is ng_provider
        
        # Cache should have 2 entries (US and one shared for CA/NG)
        assert len(_provider_instances) == 3
        assert _provider_instances["US"] is us_provider
        assert _provider_instances["CA"] is ca_provider
        assert _provider_instances["NG"] is ng_provider 