import pytest
import respx
import hmac
import hashlib
import time
import base64
import json
from httpx import Response
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import os

from app.payments.providers.rapyd import (
    RapydProvider,
    InternationalBankAccount,
    SupportedCountries,
    RapydTransactionResult
)
from app.payments.providers.constants import TransactionType, TransactionStatus

@pytest.fixture(autouse=True)
def mock_testing_env():
    with patch('app.payments.providers.rapyd.os.getenv') as mock_getenv:
        # Set TESTING to 1 for all Rapyd tests
        mock_getenv.side_effect = lambda key, default=None: "1" if key == "TESTING" else default
        yield

@pytest.fixture
def rapyd_provider():
    with patch('app.payments.providers.rapyd.os.getenv') as mock_os:
        # Use a proper side_effect that can handle the default value parameter
        mock_os.side_effect = lambda key, default=None: {
            "RAPYD_ACCESS_KEY": "test_access_key",
            "RAPYD_SECRET_KEY": "test_secret_key",
            "TESTING": "1",  # Set testing mode
        }.get(key, default)
        
        provider = RapydProvider()
        
        # Create mock API response data
        mock_payment_response = {
            "id": "payment_123",
            "status": "ACT", 
            "amount": 100,
            "currency": "USD"
        }
        
        # Use AsyncMock instead of MagicMock for the async method
        provider._make_api_request = AsyncMock(return_value=mock_payment_response)
        
        return provider

@pytest.mark.asyncio
async def test_init_with_env_vars():
    with patch('app.payments.providers.rapyd.os') as mock_os:
        mock_os.getenv.side_effect = lambda key, default=None: {
            "RAPYD_ACCESS_KEY": "test_access_key",
            "RAPYD_SECRET_KEY": "test_secret_key",
        }.get(key, default)
        provider = RapydProvider()
        assert provider.access_key == "test_access_key"
        assert provider.secret_key == "test_secret_key"
        assert provider.base_url == "https://sandboxapi.rapyd.net"

@pytest.mark.asyncio
async def test_init_missing_keys():
    with patch('app.payments.providers.rapyd.os') as mock_os:
        mock_os.getenv.return_value = None
        with pytest.raises(ValueError, match="RAPYD_ACCESS_KEY and RAPYD_SECRET_KEY"):
            RapydProvider()

@pytest.mark.asyncio
async def test_validate_international_bank_account():
    # Test with a valid account
    account = InternationalBankAccount(
        routing_number="123456789",
        account_number="12345678",
        country=SupportedCountries.CANADA,
        account_holder_name="John Doe",
        bank_name="Test Bank",
        branch_code="001"
    )
    assert account.bank_name == "Test Bank"
    assert account.account_number == "12345678"
    assert account.country_code == SupportedCountries.CANADA
    assert account.account_holder_name == "John Doe"

@pytest.mark.asyncio
async def test_validate_international_bank_account_invalid_country():
    # Test with an invalid country
    with pytest.raises(ValueError, match="Country code XYZ is not supported"):
        InternationalBankAccount(
            routing_number="123456789",
            account_number="12345678",
            country="XYZ",
            account_holder_name="John Doe"
        )

@pytest.mark.asyncio
@respx.mock
async def test_pull_success(rapyd_provider):
    # Create a mock response for the API call
    mock_response = {
        "id": "payment_123",
        "status": "CLO",
        "amount": 100,
        "currency": "CAD",
        "created_at": 1630000000
    }
    
    # Configure the mock to return this response
    rapyd_provider._make_api_request.return_value = mock_response

    bank_account = InternationalBankAccount(
        routing_number="123456789",
        account_number="12345678",
        country=SupportedCountries.CANADA,
        account_holder_name="John Doe",
        bank_name="Royal Bank",
        branch_code="001"
    )

    result = await rapyd_provider.pull(
        amount=100.0,
        currency="CAD",
        account=bank_account,
        metadata={"customer_id": "cus_123"}
    )

    assert isinstance(result, RapydTransactionResult)
    assert result.transaction_id == "payment_123"
    assert result.status == "completed"  # CLO maps to completed
    assert result.amount == 100.0
    assert result.currency == "CAD"

@pytest.mark.asyncio
@respx.mock
async def test_pull_api_error(rapyd_provider):
    # Configure the mock to raise an error
    error_message = "Invalid request parameters"
    rapyd_provider._make_api_request.side_effect = ValueError(f"Rapyd API error: 400101 - {error_message}")

    bank_account = InternationalBankAccount(
        routing_number="123456789",
        account_number="12345678",
        country=SupportedCountries.CANADA,
        account_holder_name="John Doe",
        bank_name="Royal Bank",
        branch_code="001"
    )

    with pytest.raises(ValueError, match=f"Rapyd API error: 400101 - {error_message}"):
        await rapyd_provider.pull(
            amount=100.0,
            currency="CAD",
            account=bank_account,
            metadata={"customer_id": "cus_123"}
        )

@pytest.mark.asyncio
@respx.mock
async def test_push_success(rapyd_provider):
    # Create a mock response for the API call
    mock_response = {
        "id": "payout_456",
        "status": "CMP",
        "amount": 200,
        "currency": "NGN",
        "created_at": 1630000000
    }
    
    # Configure the mock to return this response
    rapyd_provider._make_api_request.return_value = mock_response

    bank_account = InternationalBankAccount(
        routing_number="1234567890",
        account_number="1234567890",  # Valid 10-digit NUBAN for Nigeria
        country=SupportedCountries.NIGERIA,
        account_holder_name="Jane Smith",
        bank_name="Nigerian Bank"
    )

    result = await rapyd_provider.push(
        amount=200.0,
        currency="NGN",
        account=bank_account,
        metadata={"customer_id": "cus_456"}
    )

    assert isinstance(result, RapydTransactionResult)
    assert result.transaction_id == "payout_456"
    assert result.status == "completed"  # CMP maps to completed

@pytest.mark.asyncio
@respx.mock
async def test_push_api_error(rapyd_provider):
    # Configure the mock to raise an error
    error_message = "Internal server error"
    rapyd_provider._make_api_request.side_effect = ValueError(f"Rapyd API error: 500000 - {error_message}")

    bank_account = InternationalBankAccount(
        routing_number="1234567890",
        account_number="1234567890",  # Valid 10-digit NUBAN for Nigeria
        country=SupportedCountries.NIGERIA,
        account_holder_name="Jane Smith",
        bank_name="Nigerian Bank"
    )

    with pytest.raises(ValueError, match=f"Rapyd API error: 500000 - {error_message}"):
        await rapyd_provider.push(
            amount=200.0,
            currency="NGN",
            account=bank_account,
            metadata={"customer_id": "cus_456"}
        )

@pytest.mark.asyncio
@respx.mock
async def test_status_mapping(rapyd_provider):
    # Test various status mappings
    statuses = {
        "ACT": "pending",    # Active
        "CAN": "failed",     # Canceled
        "CLO": "completed",  # Closed (completed)
        "ERR": "failed",     # Error
        "EXP": "failed",     # Expired
        "PEN": "pending",    # Pending
        "CMP": "completed",  # Completed
        "NEW": "pending",    # New
        "UNK": "pending"     # Unknown (default to pending)
    }
    
    for rapyd_status, expected_status in statuses.items():
        # Create a mock response with the current status
        mock_response = {
            "id": f"payment_{rapyd_status}",
            "status": rapyd_status,
            "amount": 10,
            "currency": "USD",
            "created_at": 1630000000
        }
        
        # Configure the mock to return this response
        rapyd_provider._make_api_request.return_value = mock_response
        
        bank_account = InternationalBankAccount(
            routing_number="123456789012345678",
            account_number="123456789012345678",  # Valid 18-digit CLABE for Mexico
            country=SupportedCountries.MEXICO,
            account_holder_name="Test User",
            bank_name="Test Bank"
        )
        
        result = await rapyd_provider.pull(
            amount=10.0,
            currency="USD",
            account=bank_account,
            metadata={"customer_id": f"cus_{rapyd_status}"}
        )
        
        assert result.status == expected_status, f"Expected {expected_status} for Rapyd status {rapyd_status}"

@pytest.mark.asyncio
@respx.mock
async def test_retry_on_network_error(rapyd_provider):
    # Create side effect responses
    call_count = 0
    
    async def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        
        if call_count == 1:
            # First call fails
            raise ValueError("Network error when connecting to Rapyd API: Connection reset")
        else:
            # Second call succeeds
            return {
                "id": "payment_retry",
                "status": "ACT",
                "amount": 100,
                "currency": "MXN",
                "created_at": 1630000000
            }
    
    # Replace the mock with the side effect function
    rapyd_provider._make_api_request = AsyncMock(side_effect=side_effect)
    
    bank_account = InternationalBankAccount(
        routing_number="123456789012345678",
        account_number="123456789012345678",  # Valid 18-digit CLABE for Mexico
        country=SupportedCountries.MEXICO,
        account_holder_name="Pedro Alvarez",
        bank_name="Mexican Bank"
    )

    # Patch sleep to avoid actual delay in tests
    with patch('asyncio.sleep', return_value=None):
        result = await rapyd_provider.pull(
            amount=100.0,
            currency="MXN",
            account=bank_account,
            metadata={"customer_id": "cus_retry"}
        )
    
    assert call_count == 2
    assert result.status == "pending"  # ACT maps to pending 