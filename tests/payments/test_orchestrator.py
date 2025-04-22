import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
import asyncio

from app.payments.services.orchestrator import transfer_cross_border, _handle_transfer_fallback
from app.payments.providers.stablecoin_base import StablecoinResult

# Mock classes for testing
class MockStablecoinResult:
    def __init__(self, tx_id, status, settled_at=None):
        self.tx_id = tx_id
        self.status = status
        self.settled_at = settled_at or datetime.now()

class MockTransactionResult:
    def __init__(self, transaction_id, status, amount, currency):
        self.transaction_id = transaction_id
        self.status = status
        self.amount = amount
        self.currency = currency

@pytest.fixture
def mock_payment_service():
    with patch('app.payments.services.orchestrator.receive_fiat') as mock_receive, \
         patch('app.payments.services.orchestrator.send_fiat') as mock_send:
        
        # Configure mocks
        mock_receive.return_value = AsyncMock(
            return_value=MockTransactionResult("debit_123", "completed", 100.0, "USD")
        )()
        mock_send.return_value = AsyncMock(
            return_value=MockTransactionResult("payout_456", "completed", 100.0, "USD")
        )()
        
        yield (mock_receive, mock_send)

@pytest.fixture
def mock_stablecoin_provider():
    with patch('app.payments.services.orchestrator.get_stablecoin_provider') as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.mint = AsyncMock(
            return_value=MockStablecoinResult("mint_789", "completed")
        )
        mock_provider.redeem = AsyncMock(
            return_value=MockStablecoinResult("redeem_101", "completed")
        )
        
        mock_get_provider.return_value = mock_provider
        yield mock_provider

@pytest.mark.asyncio
async def test_transfer_cross_border_success(mock_payment_service, mock_stablecoin_provider):
    """Test successful cross-border transfer"""
    mock_receive, mock_send = mock_payment_service
    
    result = await transfer_cross_border(
        user_id="user_123",
        amount=100.0,
        src_cc="US",
        dst_cc="MX",
        currency="USD",
        chain="polygon",
        metadata={"reference": "test_transfer"}
    )
    
    # Verify all steps were completed successfully
    assert result["status"] == "completed"
    assert result["debit"].transaction_id == "debit_123"
    assert result["mint"].tx_id == "mint_789"
    assert result["redeem"].tx_id == "redeem_101"
    assert result["payout"].transaction_id == "payout_456"
    assert len(result["errors"]) == 0
    
    # Verify each function was called with expected parameters
    mock_receive.assert_called_once_with("user_123", 100.0, "USD")
    mock_stablecoin_provider.mint.assert_called_once_with(
        100.0, "USD", "polygon", {"reference": "test_transfer"}
    )
    mock_stablecoin_provider.redeem.assert_called_once_with(
        100.0, "USD", "MX", {"reference": "test_transfer"}
    )
    mock_send.assert_called_once_with("user_123", 100.0, "USD")

@pytest.mark.asyncio
async def test_transfer_cross_border_debit_failure(mock_payment_service, mock_stablecoin_provider):
    """Test failure at debit stage"""
    mock_receive, mock_send = mock_payment_service
    
    # Configure receive_fiat to fail
    mock_receive.side_effect = ValueError("Insufficient funds")
    
    result = await transfer_cross_border(
        user_id="user_123",
        amount=100.0,
        src_cc="US",
        dst_cc="MX",
        currency="USD"
    )
    
    # Verify failure is handled correctly
    assert result["status"] == "failed"
    assert result["debit"] is None
    assert result["mint"] is None
    assert result["redeem"] is None
    assert result["payout"] is None
    assert len(result["errors"]) == 1
    assert "Insufficient funds" in result["errors"][0]
    
    # Verify only the first function was called
    mock_receive.assert_called_once()
    mock_stablecoin_provider.mint.assert_not_called()
    mock_stablecoin_provider.redeem.assert_not_called()
    mock_send.assert_not_called()

@pytest.mark.asyncio
async def test_transfer_cross_border_mint_failure(mock_payment_service, mock_stablecoin_provider):
    """Test failure at mint stage with fallback handling"""
    mock_receive, mock_send = mock_payment_service
    
    # Configure mint to fail
    mock_stablecoin_provider.mint.side_effect = ValueError("Mint failed")
    
    # Mock fallback handler to verify it's called
    with patch('app.payments.services.orchestrator._handle_transfer_fallback') as mock_fallback:
        mock_fallback.return_value = AsyncMock()()
        
        result = await transfer_cross_border(
            user_id="user_123",
            amount=100.0,
            src_cc="US",
            dst_cc="MX",
            currency="USD"
        )
        
        # Verify failure is handled correctly
        assert result["status"] == "failed"
        assert result["debit"] is not None
        assert result["mint"] is None
        assert result["redeem"] is None
        assert result["payout"] is None
        assert len(result["errors"]) == 1
        assert "Mint failed" in result["errors"][0]
        
        # Verify fallback was called
        mock_fallback.assert_called_once()
        args, _ = mock_fallback.call_args
        assert args[0] == result
        assert args[1] == "user_123"
        assert args[2] == 100.0
        assert args[3] == "USD"

@pytest.mark.asyncio
async def test_transfer_cross_border_redeem_failure(mock_payment_service, mock_stablecoin_provider):
    """Test failure at redeem stage"""
    mock_receive, mock_send = mock_payment_service
    
    # Configure redeem to fail
    mock_stablecoin_provider.redeem.side_effect = ValueError("Redeem failed")
    
    # Mock fallback handler to verify it's called
    with patch('app.payments.services.orchestrator._handle_transfer_fallback') as mock_fallback:
        mock_fallback.return_value = AsyncMock()()
        
        result = await transfer_cross_border(
            user_id="user_123",
            amount=100.0,
            src_cc="US",
            dst_cc="MX",
            currency="USD"
        )
        
        # Verify failure is handled correctly
        assert result["status"] == "failed"
        assert result["debit"] is not None
        assert result["mint"] is not None
        assert result["redeem"] is None
        assert result["payout"] is None
        assert len(result["errors"]) == 1
        assert "Redeem failed" in result["errors"][0]
        
        # Verify fallback was called
        mock_fallback.assert_called_once()

@pytest.mark.asyncio
async def test_transfer_cross_border_payout_failure(mock_payment_service, mock_stablecoin_provider):
    """Test failure at payout stage"""
    mock_receive, mock_send = mock_payment_service
    
    # Configure send_fiat to fail
    mock_send.side_effect = ValueError("Payout failed")
    
    # Mock fallback handler to verify it's called
    with patch('app.payments.services.orchestrator._handle_transfer_fallback') as mock_fallback:
        mock_fallback.return_value = AsyncMock()()
        
        result = await transfer_cross_border(
            user_id="user_123",
            amount=100.0,
            src_cc="US",
            dst_cc="MX",
            currency="USD"
        )
        
        # Verify failure is handled correctly
        assert result["status"] == "failed"
        assert result["debit"] is not None
        assert result["mint"] is not None
        assert result["redeem"] is not None
        assert result["payout"] is None
        assert len(result["errors"]) == 1
        assert "Payout failed" in result["errors"][0]
        
        # Verify fallback was called
        mock_fallback.assert_called_once()

@pytest.mark.asyncio
async def test_fallback_handler_debit_only(mock_payment_service):
    """Test fallback handling when only debit succeeded"""
    mock_receive, mock_send = mock_payment_service
    
    result = {
        "debit": MockTransactionResult("debit_123", "completed", 100.0, "USD"),
        "mint": None,
        "redeem": None,
        "payout": None,
        "status": "failed",
        "errors": ["Mint operation failed"]
    }
    
    await _handle_transfer_fallback(result, "user_123", 100.0, "USD")
    
    # Verify refund was initiated
    mock_send.assert_called_once_with("user_123", 100.0, "USD", refund=True)
    assert result["status"] == "refunded"

@pytest.mark.asyncio
async def test_fallback_handler_mint_succeeded(mock_payment_service):
    """Test fallback handling when mint succeeded but redeem failed"""
    mock_receive, mock_send = mock_payment_service
    
    result = {
        "debit": MockTransactionResult("debit_123", "completed", 100.0, "USD"),
        "mint": MockStablecoinResult("mint_789", "completed"),
        "redeem": None,
        "payout": None,
        "status": "failed",
        "errors": ["Redeem operation failed"]
    }
    
    await _handle_transfer_fallback(result, "user_123", 100.0, "USD")
    
    # Verify no refund was attempted (needs manual intervention)
    mock_send.assert_not_called()
    assert result["status"] == "indeterminate_needs_review"

@pytest.mark.asyncio
async def test_fallback_handler_redeem_succeeded(mock_payment_service):
    """Test fallback handling when redeem succeeded but payout failed"""
    mock_receive, mock_send = mock_payment_service
    
    result = {
        "debit": MockTransactionResult("debit_123", "completed", 100.0, "USD"),
        "mint": MockStablecoinResult("mint_789", "completed"),
        "redeem": MockStablecoinResult("redeem_101", "completed"),
        "payout": None,
        "status": "failed",
        "errors": ["Payout operation failed"]
    }
    
    await _handle_transfer_fallback(result, "user_123", 100.0, "USD")
    
    # Verify no operations were attempted (needs manual intervention)
    mock_send.assert_not_called()
    assert result["status"] == "redemption_complete_payout_failed"

@pytest.mark.asyncio
async def test_fallback_handler_error(mock_payment_service):
    """Test fallback handler itself encountering an error"""
    mock_receive, mock_send = mock_payment_service
    
    # Configure send_fiat to fail during refund
    mock_send.side_effect = ValueError("Refund failed")
    
    result = {
        "debit": MockTransactionResult("debit_123", "completed", 100.0, "USD"),
        "mint": None,
        "redeem": None,
        "payout": None,
        "status": "failed",
        "errors": ["Primary error"]
    }
    
    # Fallback error should be caught in the main function, so directly test
    # that it raises here
    with pytest.raises(ValueError, match="Refund failed"):
        await _handle_transfer_fallback(result, "user_123", 100.0, "USD")
    
    # Verify refund was attempted
    mock_send.assert_called_once() 