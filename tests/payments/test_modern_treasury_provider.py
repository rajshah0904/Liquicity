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
    MTTransactionResult
)

@pytest.fixture
def mt_provider():
    with patch('app.payments.providers.modern_treasury.os') as mock_os:
        mock_os.getenv.return_value = "test_api_key"
        provider = ModernTreasuryProvider()
        return provider

@pytest.mark.asyncio
async def test_init_with_env_vars():
    with patch('app.payments.providers.modern_treasury.os') as mock_os:
        mock_os.getenv.return_value = "test_api_key"
        provider = ModernTreasuryProvider()
        assert provider.api_key == "test_api_key"
        assert provider.base_url == "https://api.moderntreasury.com/api"
        assert provider.version == "v1"

@pytest.mark.asyncio
async def test_init_missing_api_key():
    with patch('app.payments.providers.modern_treasury.os') as mock_os:
        mock_os.getenv.return_value = None
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
    respx.post("https://api.moderntreasury.com/api/v1/payment_orders").mock(
        return_value=Response(
            200,
            json={
                "id": "po_123",
                "status": "pending",
                "amount": 100,
                "currency": "USD",
                "direction": "debit",
                "rails": "ach",
                "created_at": "2023-01-01T00:00:00Z"
            }
        )
    )

    bank_account = USBankAccount(
        account_number="12345678",
        routing_number="021000021",
        account_type="checking"
    )

    result = await mt_provider.pull(
        amount=100.0,
        currency="USD",
        bank_account=bank_account,
        customer_id="cus_123",
        rails=USPaymentRailType.ACH
    )

    assert isinstance(result, MTTransactionResult)
    assert result.transaction_id == "po_123"
    assert result.status == "pending"
    assert result.amount == 100.0
    assert result.currency == "USD"
    assert result.rails == "ach"

@pytest.mark.asyncio
@respx.mock
async def test_pull_api_error(mt_provider):
    respx.post("https://api.moderntreasury.com/api/v1/payment_orders").mock(
        return_value=Response(
            400,
            json={
                "error": {
                    "message": "Invalid request",
                    "type": "invalid_request"
                }
            }
        )
    )

    bank_account = USBankAccount(
        account_number="12345678",
        routing_number="021000021",
        account_type="checking"
    )

    with pytest.raises(ValueError, match="API error: Invalid request"):
        await mt_provider.pull(
            amount=100.0,
            currency="USD",
            bank_account=bank_account,
            customer_id="cus_123"
        )

@pytest.mark.asyncio
@respx.mock
async def test_push_success(mt_provider):
    respx.post("https://api.moderntreasury.com/api/v1/payment_orders").mock(
        return_value=Response(
            200,
            json={
                "id": "po_456",
                "status": "pending",
                "amount": 200,
                "currency": "USD",
                "direction": "credit",
                "rails": "wire",
                "created_at": "2023-01-01T00:00:00Z"
            }
        )
    )

    bank_account = USBankAccount(
        account_number="87654321",
        routing_number="021000021",
        account_type="savings"
    )

    result = await mt_provider.push(
        amount=200.0,
        currency="USD",
        bank_account=bank_account,
        customer_id="cus_456",
        rails=USPaymentRailType.WIRE
    )

    assert isinstance(result, MTTransactionResult)
    assert result.transaction_id == "po_456"
    assert result.status == "pending"
    assert result.amount == 200.0
    assert result.currency == "USD"
    assert result.rails == "wire"

@pytest.mark.asyncio
@respx.mock
async def test_push_api_error(mt_provider):
    respx.post("https://api.moderntreasury.com/api/v1/payment_orders").mock(
        return_value=Response(
            500,
            json={
                "error": {
                    "message": "Internal server error",
                    "type": "server_error"
                }
            }
        )
    )

    bank_account = USBankAccount(
        account_number="87654321",
        routing_number="021000021",
        account_type="savings"
    )

    with pytest.raises(ValueError, match="API error: Internal server error"):
        await mt_provider.push(
            amount=200.0,
            currency="USD",
            bank_account=bank_account,
            customer_id="cus_456"
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

    # Test with a large amount that should use ACH
    result = await mt_provider.push(
        amount=500.0,
        currency="USD",
        bank_account=bank_account,
        customer_id="cus_789",
        smart_rails=True
    )

    assert result.rails == "rtp"

@pytest.mark.asyncio
@respx.mock
async def test_retry_on_network_error(mt_provider):
    # Mock a network error followed by a successful response
    mock_call = respx.post("https://api.moderntreasury.com/api/v1/payment_orders")
    
    # Set up the mock to fail on first call, succeed on second
    mock_responses = [
        Response(
            503,
            json={"error": {"message": "Service unavailable"}}
        ),
        Response(
            200,
            json={
                "id": "po_retry",
                "status": "pending",
                "amount": 100,
                "currency": "USD",
                "direction": "debit",
                "rails": "ach",
                "created_at": "2023-01-01T00:00:00Z"
            }
        )
    ]
    
    mock_call.side_effect = mock_responses
    
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
            bank_account=bank_account,
            customer_id="cus_retry"
        )
    
    assert mock_call.call_count == 2
    assert result.transaction_id == "po_retry" 