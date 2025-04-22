import pytest
import respx
import hmac
import hashlib
import time
import base64
import json
from httpx import Response
import asyncio
from unittest.mock import patch, MagicMock

from app.payments.providers.rapyd import (
    RapydProvider,
    InternationalBankAccount,
    SupportedCountries,
    RapydTransactionResult
)

@pytest.fixture
def rapyd_provider():
    with patch('app.payments.providers.rapyd.os') as mock_os:
        mock_os.getenv.side_effect = lambda x: {
            "RAPYD_ACCESS_KEY": "test_access_key",
            "RAPYD_SECRET_KEY": "test_secret_key",
        }.get(x)
        provider = RapydProvider()
        # Mock the _generate_signature method to avoid real signature generation
        provider._generate_signature = MagicMock(return_value="test_signature")
        return provider

@pytest.mark.asyncio
async def test_init_with_env_vars():
    with patch('app.payments.providers.rapyd.os') as mock_os:
        mock_os.getenv.side_effect = lambda x: {
            "RAPYD_ACCESS_KEY": "test_access_key",
            "RAPYD_SECRET_KEY": "test_secret_key",
        }.get(x)
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
        bank_name="Test Bank",
        account_number="12345678",
        country=SupportedCountries.CANADA,
        account_holder_name="John Doe",
        branch_code="001"
    )
    assert account.bank_name == "Test Bank"
    assert account.account_number == "12345678"
    assert account.country == "CA"
    assert account.account_holder_name == "John Doe"

@pytest.mark.asyncio
async def test_validate_international_bank_account_invalid_country():
    # Test with an invalid country
    with pytest.raises(ValueError, match="country must be"):
        InternationalBankAccount(
            bank_name="Test Bank",
            account_number="12345678",
            country="INVALID",
            account_holder_name="John Doe"
        )

@pytest.mark.asyncio
@respx.mock
async def test_pull_success(rapyd_provider):
    # Mock the collect payment API response
    respx.post("https://sandboxapi.rapyd.net/v1/payments").mock(
        return_value=Response(
            200,
            json={
                "status": {
                    "status": "SUCCESS",
                    "message": "Payment created",
                    "error_code": ""
                },
                "data": {
                    "id": "payment_123",
                    "status": "CLO",
                    "amount": 100,
                    "currency": "CAD",
                    "created_at": 1630000000
                }
            }
        )
    )

    bank_account = InternationalBankAccount(
        bank_name="Royal Bank",
        account_number="12345678",
        country=SupportedCountries.CANADA,
        account_holder_name="John Doe",
        branch_code="001"
    )

    result = await rapyd_provider.pull(
        amount=100.0,
        currency="CAD",
        bank_account=bank_account,
        customer_id="cus_123"
    )

    assert isinstance(result, RapydTransactionResult)
    assert result.transaction_id == "payment_123"
    assert result.status == "completed"  # CLO maps to completed
    assert result.amount == 100.0
    assert result.currency == "CAD"

@pytest.mark.asyncio
@respx.mock
async def test_pull_api_error(rapyd_provider):
    # Mock an API error response
    respx.post("https://sandboxapi.rapyd.net/v1/payments").mock(
        return_value=Response(
            400,
            json={
                "status": {
                    "status": "ERROR",
                    "message": "Invalid request parameters",
                    "error_code": "400101"
                }
            }
        )
    )

    bank_account = InternationalBankAccount(
        bank_name="Royal Bank",
        account_number="12345678",
        country=SupportedCountries.CANADA,
        account_holder_name="John Doe",
        branch_code="001"
    )

    with pytest.raises(ValueError, match="API error: Invalid request parameters"):
        await rapyd_provider.pull(
            amount=100.0,
            currency="CAD",
            bank_account=bank_account,
            customer_id="cus_123"
        )

@pytest.mark.asyncio
@respx.mock
async def test_push_success(rapyd_provider):
    # Mock the create payout API response
    respx.post("https://sandboxapi.rapyd.net/v1/payouts").mock(
        return_value=Response(
            200,
            json={
                "status": {
                    "status": "SUCCESS",
                    "message": "Payout created",
                    "error_code": ""
                },
                "data": {
                    "id": "payout_456",
                    "status": "CMP",
                    "amount": 200,
                    "currency": "NGN",
                    "created_at": 1630000000
                }
            }
        )
    )

    bank_account = InternationalBankAccount(
        bank_name="Nigerian Bank",
        account_number="87654321",
        country=SupportedCountries.NIGERIA,
        account_holder_name="Jane Smith"
    )

    result = await rapyd_provider.push(
        amount=200.0,
        currency="NGN",
        bank_account=bank_account,
        customer_id="cus_456"
    )

    assert isinstance(result, RapydTransactionResult)
    assert result.transaction_id == "payout_456"
    assert result.status == "completed"  # CMP maps to completed
    assert result.amount == 200.0
    assert result.currency == "NGN"

@pytest.mark.asyncio
@respx.mock
async def test_push_api_error(rapyd_provider):
    # Mock an API error response
    respx.post("https://sandboxapi.rapyd.net/v1/payouts").mock(
        return_value=Response(
            500,
            json={
                "status": {
                    "status": "ERROR",
                    "message": "Internal server error",
                    "error_code": "500000"
                }
            }
        )
    )

    bank_account = InternationalBankAccount(
        bank_name="Nigerian Bank",
        account_number="87654321",
        country=SupportedCountries.NIGERIA,
        account_holder_name="Jane Smith"
    )

    with pytest.raises(ValueError, match="API error: Internal server error"):
        await rapyd_provider.push(
            amount=200.0,
            currency="NGN",
            bank_account=bank_account,
            customer_id="cus_456"
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
        respx.post("https://sandboxapi.rapyd.net/v1/payments").mock(
            return_value=Response(
                200,
                json={
                    "status": {
                        "status": "SUCCESS",
                        "message": "Payment created",
                        "error_code": ""
                    },
                    "data": {
                        "id": f"payment_{rapyd_status}",
                        "status": rapyd_status,
                        "amount": 10,
                        "currency": "USD",
                        "created_at": 1630000000
                    }
                }
            )
        )
        
        bank_account = InternationalBankAccount(
            bank_name="Test Bank",
            account_number="12345678",
            country=SupportedCountries.MEXICO,
            account_holder_name="Test User"
        )
        
        result = await rapyd_provider.pull(
            amount=10.0,
            currency="USD",
            bank_account=bank_account,
            customer_id=f"cus_{rapyd_status}"
        )
        
        assert result.status == expected_status, f"Expected {expected_status} for Rapyd status {rapyd_status}"

@pytest.mark.asyncio
@respx.mock
async def test_retry_on_network_error(rapyd_provider):
    # Mock a network error followed by a successful response
    mock_call = respx.post("https://sandboxapi.rapyd.net/v1/payments")
    
    # Set up the mock to fail on first call, succeed on second
    mock_responses = [
        Response(
            503,
            json={
                "status": {
                    "status": "ERROR",
                    "message": "Service unavailable",
                    "error_code": "503000"
                }
            }
        ),
        Response(
            200,
            json={
                "status": {
                    "status": "SUCCESS",
                    "message": "Payment created",
                    "error_code": ""
                },
                "data": {
                    "id": "payment_retry",
                    "status": "ACT",
                    "amount": 100,
                    "currency": "MXN",
                    "created_at": 1630000000
                }
            }
        )
    ]
    
    mock_call.side_effect = mock_responses
    
    bank_account = InternationalBankAccount(
        bank_name="Mexican Bank",
        account_number="12345678",
        country=SupportedCountries.MEXICO,
        account_holder_name="Pedro Alvarez"
    )

    # Patch sleep to avoid actual delay in tests
    with patch('asyncio.sleep', return_value=None):
        result = await rapyd_provider.pull(
            amount=100.0,
            currency="MXN",
            bank_account=bank_account,
            customer_id="cus_retry"
        )
    
    assert mock_call.call_count == 2
    assert result.transaction_id == "payment_retry"
    assert result.status == "pending"  # ACT maps to pending 