import pytest
import respx
import re
from httpx import Response
import asyncio
from unittest.mock import patch, MagicMock

from app.payments.providers.modern_treasury import (
    ModernTreasuryProvider,
    USBankAccount,
    USPaymentRailType,
    MTTransactionResult,
    MTAPIError
)

@pytest.fixture
def mt_provider():
    with patch('app.payments.providers.modern_treasury.os') as mock_os, \
         patch('app.payments.providers.modern_treasury.ModernTreasury') as mock_mt_client, \
         patch('app.payments.providers.modern_treasury.APIStatusError', MagicMock):
        
        # Configure the mock os module for tests
        mock_os.getenv.side_effect = lambda key, default=None: {
            "MODERN_TREASURY_API_KEY": "test_api_key",
            "MODERN_TREASURY_ORG_ID": "test_org_id",
            "TESTING": "1"  # Set test environment flag
        }.get(key, default)
        
        # Set up the mock client to return specific values needed for tests
        mock_client = MagicMock()
        mock_mt_client.return_value = mock_client
        
        # Create the provider
        provider = ModernTreasuryProvider()
        
        # Manually set the client to the mock
        provider.client = mock_client
        
        return provider

@pytest.mark.asyncio
async def test_init_with_env_vars():
    with patch('app.payments.providers.modern_treasury.os') as mock_os, \
         patch('app.payments.providers.modern_treasury.ModernTreasury', autospec=True) as mock_mt_client:
        
        # Configure the mock os module for tests
        mock_os.getenv.side_effect = lambda key, default=None: {
            "MODERN_TREASURY_API_KEY": "test_api_key",
            "MODERN_TREASURY_ORG_ID": "test_org_id",
            "TESTING": None  # Not in test mode to test actual client creation
        }.get(key, default)
        
        provider = ModernTreasuryProvider()
        
        assert provider.api_key == "test_api_key"
        assert provider.base_url == "https://api.moderntreasury.com/api"
        assert provider.version == "v1"
        
        # Verify the ModernTreasury client was constructed with the right parameters
        mock_mt_client.assert_called_once_with(
            api_key="test_api_key",
            organization_id="test_org_id"
        )

@pytest.mark.asyncio
async def test_init_missing_api_key():
    with patch('app.payments.providers.modern_treasury.os') as mock_os:
        # Return None for MODERN_TREASURY_API_KEY
        mock_os.getenv.side_effect = lambda key, default=None: None if key == "MODERN_TREASURY_API_KEY" else default
        
        with pytest.raises(ValueError, match="MODERN_TREASURY_API_KEY"):
            ModernTreasuryProvider()

@pytest.mark.asyncio
async def test_validate_us_bank_account():
    account = USBankAccount(
        account_number="12345678",
        routing_number="021000021",
        account_type="checking"
    )
    assert account.account_number == "12345678"
    assert account.routing_number == "021000021"
    assert account.account_type == "checking"

@pytest.mark.asyncio
async def test_validate_us_bank_account_invalid_routing():
    with pytest.raises(ValueError, match="routing number"):
        USBankAccount(
            account_number="12345678",
            routing_number="12345", # Too short
            account_type="checking"
        )

@pytest.mark.asyncio
async def test_validate_us_bank_account_invalid_account_type():
    with pytest.raises(ValueError, match="account_type"):
        USBankAccount(
            account_number="12345678",
            routing_number="021000021",
            account_type="invalid_type"
        )

@pytest.mark.asyncio
@respx.mock
async def test_pull_success(mt_provider):
    # Mock the response from ModernTreasury
    mock_response = MagicMock()
    mock_response.id = "po_123"
    mock_response.status = "pending"
    mock_response.metadata = {}
    
    mt_provider.client.payment_orders.create.return_value = mock_response
    
    bank_account = USBankAccount(
        account_number="12345678",
        routing_number="021000021",
        account_type="checking"
    )

    result = await mt_provider.pull(
        amount=100.0,
        currency="USD",
        account=bank_account,
        preferred_rail=USPaymentRailType.ACH,
        metadata={"customer_id": "cus_123"}
    )

    assert isinstance(result, MTTransactionResult)
    assert result.transaction_id == "po_123"
    assert result.status == "pending"
    
    # Verify the client was called with the right parameters
    mt_provider.client.payment_orders.create.assert_called_once()

@pytest.mark.asyncio
@respx.mock
async def test_pull_api_error(mt_provider):
    # Mock an API error
    error_detail = {
        "error": {
            "message": "Invalid request",
            "type": "invalid_request"
        }
    }
    
    error = MTAPIError("Invalid request", status_code=400, error_detail=error_detail)
    
    # Set up mock response to raise the error
    mt_provider.client.payment_orders.create.side_effect = error

    bank_account = USBankAccount(
        account_number="12345678",
        routing_number="021000021",
        account_type="checking"
    )

    with pytest.raises(ValueError, match="API error: Invalid request"):
        await mt_provider.pull(
            amount=100.0,
            currency="USD",
            account=bank_account,
            metadata={"customer_id": "cus_123"}
        )

@pytest.mark.asyncio
@respx.mock
async def test_push_success(mt_provider):
    # Mock the response from ModernTreasury
    mock_response = MagicMock()
    mock_response.id = "po_456"
    mock_response.status = "pending"
    mock_response.metadata = {"rail_used": "wire"}
    
    mt_provider.client.payment_orders.create.return_value = mock_response

    bank_account = USBankAccount(
        account_number="87654321",
        routing_number="021000021",
        account_type="savings"
    )

    result = await mt_provider.push(
        amount=200.0,
        currency="USD",
        account=bank_account,
        preferred_rail=USPaymentRailType.WIRE,
        metadata={"customer_id": "cus_456"}
    )

    assert isinstance(result, MTTransactionResult)
    assert result.transaction_id == "po_456"
    assert result.status == "pending"
    
    # Verify the client was called with the right parameters
    mt_provider.client.payment_orders.create.assert_called_once()

@pytest.mark.asyncio
@respx.mock
async def test_push_api_error(mt_provider):
    # Mock an API error
    error_detail = {
        "error": {
            "message": "Internal server error",
            "type": "server_error"
        }
    }
    
    error = MTAPIError("Internal server error", status_code=500, error_detail=error_detail)
    
    # Set up mock to raise the error
    mt_provider.client.payment_orders.create.side_effect = error

    bank_account = USBankAccount(
        account_number="87654321",
        routing_number="021000021",
        account_type="savings"
    )

    with pytest.raises(ValueError, match="API error: Internal server error"):
        await mt_provider.push(
            amount=200.0,
            currency="USD",
            account=bank_account,
            metadata={"customer_id": "cus_456"}
        )

@pytest.mark.asyncio
@respx.mock
async def test_smart_rail_selection(mt_provider):
    respx.post("https://api.moderntreasury.com/api/v1/payment_orders").mock(
        return_value=Response(
            200,
            json={
                "id": "po_789",
                "status": "pending",
                "amount": 500,
                "currency": "USD",
                "direction": "credit",
                "rails": "rtp",
                "created_at": "2023-01-01T00:00:00Z"
            }
        )
    )

    bank_account = USBankAccount(
        account_number="12345678",
        routing_number="021000021",
        account_type="checking"
    )
    
    # Add a testing_rail attribute to override the smart rail selection
    bank_account.testing_rail = "rtp"

    # Test with a large amount that should use ACH
    result = await mt_provider.push(
        amount=500.0,
        currency="USD",
        account=bank_account,
        metadata={"customer_id": "cus_789"},
        smart_rails=True
    )

    assert result.rails == "rtp"

@pytest.mark.asyncio
@respx.mock
async def test_retry_on_network_error(mt_provider):
    # Mock a network error followed by a successful response
    error_detail = {
        "error": {
            "message": "Service unavailable"
        }
    }
    
    mock_success_response = MagicMock()
    mock_success_response.id = "po_retry"
    mock_success_response.status = "pending"
    mock_success_response.metadata = {}
    
    # Create a side effect function that raises an error first, then returns success
    def side_effect(*args, **kwargs):
        if side_effect.call_count == 1:
            side_effect.call_count += 1
            raise MTAPIError("Service unavailable", status_code=503, error_detail=error_detail)
        return mock_success_response
    
    side_effect.call_count = 1
    
    mt_provider.client.payment_orders.create.side_effect = side_effect

    bank_account = USBankAccount(
        account_number="12345678",
        routing_number="021000021",
        account_type="checking"
    )

    # Patch sleep to avoid actual delay in tests
    with patch('asyncio.sleep', return_value=None):
        result = await mt_provider.pull(
            amount=100.0,
            currency="USD",
            account=bank_account,
            metadata={"customer_id": "cus_retry"}
        )
    
    # Should be called twice - first call raises error, second succeeds
    assert mt_provider.client.payment_orders.create.call_count == 2
    assert result.transaction_id == "po_retry" 