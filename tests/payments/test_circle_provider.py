import pytest
import respx
from httpx import Response
import asyncio
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from app.payments.providers.circle_provider import (
    CircleProvider,
    CircleStablecoinResult,
    CircleAPIError,
    CircleNetworkError,
    CircleTimeoutError
)

@pytest.fixture
def circle_provider():
    with patch('app.payments.providers.circle_provider.os') as mock_os:
        mock_os.getenv.return_value = "test_api_key"
        provider = CircleProvider()
        return provider

@pytest.mark.asyncio
async def test_init_with_env_vars():
    with patch('app.payments.providers.circle_provider.os') as mock_os:
        mock_os.getenv.return_value = "test_api_key"
        provider = CircleProvider()
        assert provider.client.api_key == "test_api_key"
        assert provider.max_retries == 3
        assert provider.retry_delay == 1

@pytest.mark.asyncio
async def test_init_missing_api_key():
    with patch('app.payments.providers.circle_provider.os') as mock_os:
        mock_os.getenv.return_value = None
        with pytest.raises(ValueError, match="CIRCLE_API_KEY environment variable is not set"):
            CircleProvider()

@pytest.mark.asyncio
async def test_status_mapping(circle_provider):
    # Test various status mappings
    assert circle_provider._map_status("pending") == "pending"
    assert circle_provider._map_status("complete") == "completed"
    assert circle_provider._map_status("failed") == "failed"
    assert circle_provider._map_status("processing") == "pending"
    assert circle_provider._map_status("success") == "completed"
    assert circle_provider._map_status("error") == "failed"
    assert circle_provider._map_status("unknown_status") == "pending"  # Default

@pytest.mark.asyncio
async def test_parse_datetime(circle_provider):
    # Test ISO datetime parsing
    iso_date = "2023-01-01T12:00:00Z"
    expected_datetime = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    
    parsed = circle_provider._parse_datetime(iso_date)
    assert parsed == expected_datetime
    
    # Test with None
    assert circle_provider._parse_datetime(None) is None
    
    # Test with invalid format
    assert circle_provider._parse_datetime("invalid-date") is None

@pytest.mark.asyncio
@respx.mock
async def test_mint_success(circle_provider):
    # Mock successful mint API call
    respx.post("https://api.circle.com/v1/stablecoins/mint").mock(
        return_value=Response(
            200,
            json={
                "id": "mint_123",
                "status": "pending",
                "amount": "100",
                "currency": "USD",
                "chain": "polygon",
                "createdAt": "2023-01-01T12:00:00Z"
            }
        )
    )

    result = await circle_provider.mint(
        amount=100.0,
        currency="USD",
        chain="polygon",
        metadata={"reference": "test-mint"}
    )

    assert isinstance(result, CircleStablecoinResult)
    assert result.tx_id == "mint_123"
    assert result.status == "pending"
    assert isinstance(result.settled_at, datetime)

@pytest.mark.asyncio
@respx.mock
async def test_mint_api_error(circle_provider):
    # Mock API error response
    respx.post("https://api.circle.com/v1/stablecoins/mint").mock(
        return_value=Response(
            400,
            json={
                "code": "invalid_request",
                "message": "Invalid request parameters"
            }
        )
    )

    with pytest.raises(ValueError, match="Circle API error: Invalid request parameters"):
        await circle_provider.mint(
            amount=100.0,
            currency="USD",
            chain="polygon"
        )

@pytest.mark.asyncio
@respx.mock
async def test_redeem_success(circle_provider):
    # Mock successful redeem API call
    respx.post("https://api.circle.com/v1/stablecoins/redeem").mock(
        return_value=Response(
            200,
            json={
                "id": "redeem_456",
                "status": "complete",
                "amount": "200",
                "currency": "USD",
                "bankAccountId": "bank_123",
                "createdAt": "2023-01-01T12:00:00Z"
            }
        )
    )

    result = await circle_provider.redeem(
        amount=200.0,
        currency="USD",
        bank_account_id="bank_123",
        metadata={"reference": "test-redeem"}
    )

    assert isinstance(result, CircleStablecoinResult)
    assert result.tx_id == "redeem_456"
    assert result.status == "completed"  # complete maps to completed
    assert isinstance(result.settled_at, datetime)

@pytest.mark.asyncio
@respx.mock
async def test_redeem_api_error(circle_provider):
    # Mock API error response
    respx.post("https://api.circle.com/v1/stablecoins/redeem").mock(
        return_value=Response(
            500,
            json={
                "code": "server_error",
                "message": "Internal server error"
            }
        )
    )

    with pytest.raises(ValueError, match="Circle API error: Internal server error"):
        await circle_provider.redeem(
            amount=200.0,
            currency="USD",
            bank_account_id="bank_123"
        )

@pytest.mark.asyncio
@respx.mock
async def test_get_balance_success(circle_provider):
    # Mock successful balance API call
    respx.get("https://api.circle.com/v1/wallets/balance").mock(
        return_value=Response(
            200,
            json={
                "balances": [
                    {
                        "token": "USDC",
                        "amount": "1000.5",
                        "updated_at": "2023-01-01T12:00:00Z"
                    },
                    {
                        "token": "ETH",
                        "amount": "0.5",
                        "updated_at": "2023-01-01T12:00:00Z"
                    }
                ]
            }
        )
    )

    balance = await circle_provider.get_balance(
        wallet_address="0x1234567890abcdef",
        chain="ethereum"
    )

    assert balance == 1000.5  # Should find and convert the USDC balance

@pytest.mark.asyncio
@respx.mock
async def test_get_balance_empty(circle_provider):
    # Mock API response with no USDC balance
    respx.get("https://api.circle.com/v1/wallets/balance").mock(
        return_value=Response(
            200,
            json={
                "balances": [
                    {
                        "token": "ETH",
                        "amount": "0.5",
                        "updated_at": "2023-01-01T12:00:00Z"
                    }
                ]
            }
        )
    )

    balance = await circle_provider.get_balance(
        wallet_address="0x1234567890abcdef"
    )

    assert balance == 0.0  # Should return 0 when no USDC found

@pytest.mark.asyncio
@respx.mock
async def test_get_transaction_status_success(circle_provider):
    # Mock successful transaction status API call
    respx.get("https://api.circle.com/v1/transactions/tx_789").mock(
        return_value=Response(
            200,
            json={
                "id": "tx_789",
                "status": "complete",
                "createdAt": "2023-01-01T12:00:00Z"
            }
        )
    )

    status = await circle_provider.get_transaction_status("tx_789")
    assert status == "completed"  # complete maps to completed

@pytest.mark.asyncio
@respx.mock
async def test_get_transaction_status_error(circle_provider):
    # Mock API error response
    respx.get("https://api.circle.com/v1/transactions/tx_invalid").mock(
        return_value=Response(
            404,
            json={
                "code": "not_found",
                "message": "Transaction not found"
            }
        )
    )

    with pytest.raises(ValueError, match="Circle API error: Transaction not found"):
        await circle_provider.get_transaction_status("tx_invalid")

@pytest.mark.asyncio
@respx.mock
async def test_get_supported_chains_success(circle_provider):
    # Mock successful chains API call
    respx.get("https://api.circle.com/v1/chains").mock(
        return_value=Response(
            200,
            json={
                "chains": [
                    {"id": "ethereum", "name": "Ethereum"},
                    {"id": "polygon", "name": "Polygon"},
                    {"id": "solana", "name": "Solana"}
                ]
            }
        )
    )

    chains = await circle_provider.get_supported_chains()
    assert "ethereum" in chains
    assert "polygon" in chains
    assert "solana" in chains
    assert len(chains) == 3

@pytest.mark.asyncio
@respx.mock
async def test_get_transaction_history_success(circle_provider):
    # Mock successful history API call
    respx.get("https://api.circle.com/v1/transactions").mock(
        return_value=Response(
            200,
            json={
                "items": [
                    {
                        "id": "tx_1",
                        "status": "complete",
                        "amount": "100",
                        "createdAt": "2023-01-01T12:00:00Z"
                    },
                    {
                        "id": "tx_2",
                        "status": "pending",
                        "amount": "200",
                        "createdAt": "2023-01-01T13:00:00Z"
                    }
                ],
                "hasMore": False
            }
        )
    )

    history = await circle_provider.get_transaction_history(
        page_size=10,
        page_number=1
    )
    
    assert len(history) == 2
    assert history[0]["id"] == "tx_1"
    assert history[1]["id"] == "tx_2"

@pytest.mark.asyncio
@respx.mock
async def test_retry_on_timeout(circle_provider):
    # Mock a timeout error followed by a successful response
    mock_call = respx.post("https://api.circle.com/v1/stablecoins/mint")
    
    # Prepare side effect that will raise a timeout on first call, then succeed
    def side_effect(*args, **kwargs):
        if mock_call.call_count == 0:
            raise CircleTimeoutError("Connection timeout")
        return Response(
            200,
            json={
                "id": "mint_retry",
                "status": "pending",
                "amount": "100",
                "currency": "USD",
                "chain": "polygon",
                "createdAt": "2023-01-01T12:00:00Z"
            }
        )
    
    mock_call.side_effect = side_effect
    
    # Patch sleep to avoid actual delay in tests
    with patch('asyncio.sleep', return_value=None):
        result = await circle_provider.mint(
            amount=100.0,
            currency="USD",
            chain="polygon"
        )
    
    assert mock_call.call_count == 2
    assert result.tx_id == "mint_retry"

@pytest.mark.asyncio
@respx.mock
async def test_retry_on_network_error(circle_provider):
    # Mock a network error followed by a successful response
    mock_call = respx.post("https://api.circle.com/v1/stablecoins/redeem")
    
    # Prepare side effect that will raise a network error on first call, then succeed
    def side_effect(*args, **kwargs):
        if mock_call.call_count == 0:
            raise CircleNetworkError("Connection reset")
        return Response(
            200,
            json={
                "id": "redeem_retry",
                "status": "pending",
                "amount": "200",
                "currency": "USD",
                "bankAccountId": "bank_123",
                "createdAt": "2023-01-01T12:00:00Z"
            }
        )
    
    mock_call.side_effect = side_effect
    
    # Patch sleep to avoid actual delay in tests
    with patch('asyncio.sleep', return_value=None):
        result = await circle_provider.redeem(
            amount=200.0,
            currency="USD",
            bank_account_id="bank_123"
        )
    
    assert mock_call.call_count == 2
    assert result.tx_id == "redeem_retry"

@pytest.mark.asyncio
@respx.mock
async def test_max_retries_exceeded(circle_provider):
    # Mock a server error that persists through all retries
    mock_call = respx.post("https://api.circle.com/v1/stablecoins/mint")
    
    # Always return a 500 error
    mock_call.return_value = Response(
        500,
        json={"code": "server_error", "message": "Internal server error"}
    )
    
    # Patch sleep to avoid actual delay in tests
    with patch('asyncio.sleep', return_value=None):
        with pytest.raises(ValueError, match="Failed to mint_usdc after multiple retries"):
            await circle_provider.mint(
                amount=100.0,
                currency="USD",
                chain="polygon"
            )
    
    # Should have tried max_retries + 1 times (initial try + retries)
    assert mock_call.call_count == circle_provider.max_retries + 1 