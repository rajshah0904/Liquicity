"""Unit tests for VelaFi monitor service."""
import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import select

from clean_backend.models.velafi_order import VelafiDirection, VelafiOrder, VelafiStatus
from clean_backend.services.velafi_monitor import VelaFiMonitor
from clean_backend.services.velafi_service import VelaFiError

# Test data
TEST_USER_ID = "test_user_id"
TEST_ORDER_ID = "test_order_id"

@pytest.fixture
def mock_db_session():
    """Create mock database session."""
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session

@pytest.fixture
def mock_velafi_service():
    """Create mock VelaFi service."""
    service = MagicMock()
    service.get_order = AsyncMock()
    return service

@pytest.fixture
def monitor(mock_db_session, mock_velafi_service):
    """Create VelaFiMonitor instance with mocked dependencies."""
    monitor = VelaFiMonitor(mock_db_session)
    monitor.service = mock_velafi_service
    return monitor

def create_test_order(
    order_id: str = TEST_ORDER_ID,
    status: VelafiStatus = VelafiStatus.PENDING,
    created_at: datetime = None
) -> VelafiOrder:
    """Create a test VelafiOrder instance."""
    if created_at is None:
        created_at = datetime.now(timezone.utc) - timedelta(minutes=15)
    
    return VelafiOrder(
        order_id=order_id,
        user_id=TEST_USER_ID,
        direction=VelafiDirection.BUY,
        fiat_amount=Decimal("1000.00"),
        fiat_currency="BRL",
        usdc_amount=Decimal("200.00"),
        fx_rate=Decimal("5.00"),
        fee_usd=Decimal("2.00"),
        rail="pix",
        status=status,
        created_at=created_at
    )

@pytest.mark.asyncio
async def test_get_pending_orders(monitor):
    """Test fetching pending orders."""
    # Create test orders
    orders = [
        create_test_order(order_id="order1", status=VelafiStatus.PENDING),
        create_test_order(order_id="order2", status=VelafiStatus.PROCESSING),
        create_test_order(order_id="order3", status=VelafiStatus.COMPLETED)
    ]
    
    # Mock database query result
    mock_result = MagicMock()
    mock_result.scalars = MagicMock(return_value=MagicMock(all=lambda: orders[:2]))
    monitor.db.execute.return_value = mock_result
    
    # Get pending orders
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)
    result = await monitor._get_pending_orders(cutoff)
    
    # Verify result
    assert len(result) == 2
    assert result[0].order_id == "order1"
    assert result[1].order_id == "order2"
    
    # Verify query
    monitor.db.execute.assert_called_once()
    args = monitor.db.execute.call_args[0][0]
    assert isinstance(args, select)

@pytest.mark.asyncio
async def test_update_order_status(monitor):
    """Test updating order status."""
    # Create test order
    order = create_test_order()
    
    # Mock VelaFi API response
    monitor.service.get_order.return_value = {
        "status": "completed",
        "tx_hash": "0x1234..."
    }
    
    # Update order status
    new_status = await monitor._update_order_status(order)
    
    # Verify result
    assert new_status == VelafiStatus.COMPLETED
    assert order.status == VelafiStatus.COMPLETED
    assert order.tx_hash == "0x1234..."
    
    # Verify API call and database operations
    monitor.service.get_order.assert_called_once_with(TEST_ORDER_ID)
    monitor.db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_update_order_status_unchanged(monitor):
    """Test handling unchanged order status."""
    # Create test order
    order = create_test_order()
    
    # Mock VelaFi API response with same status
    monitor.service.get_order.return_value = {
        "status": "pending"
    }
    
    # Update order status
    new_status = await monitor._update_order_status(order)
    
    # Verify no changes
    assert new_status is None
    assert order.status == VelafiStatus.PENDING
    assert order.tx_hash is None
    
    # Verify API call but no database operations
    monitor.service.get_order.assert_called_once_with(TEST_ORDER_ID)
    monitor.db.commit.assert_not_called()

@pytest.mark.asyncio
async def test_update_order_status_retry(monitor):
    """Test retry logic for failed API calls."""
    # Create test order
    order = create_test_order()
    
    # Mock VelaFi API to fail twice then succeed
    monitor.service.get_order.side_effect = [
        VelaFiError("API error"),
        VelaFiError("API error"),
        {"status": "completed", "tx_hash": "0x1234..."}
    ]
    
    # Reduce retry delay for testing
    monitor.base_delay = 0.1
    
    # Update order status
    new_status = await monitor._update_order_status(order)
    
    # Verify eventual success
    assert new_status == VelafiStatus.COMPLETED
    assert order.status == VelafiStatus.COMPLETED
    assert order.tx_hash == "0x1234..."
    
    # Verify retry attempts
    assert monitor.service.get_order.call_count == 3
    monitor.db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_update_order_status_max_retries(monitor):
    """Test handling max retries exceeded."""
    # Create test order
    order = create_test_order()
    
    # Mock VelaFi API to always fail
    monitor.service.get_order.side_effect = VelaFiError("API error")
    
    # Reduce retry delay for testing
    monitor.base_delay = 0.1
    
    # Update order status
    new_status = await monitor._update_order_status(order)
    
    # Verify failure
    assert new_status is None
    assert order.status == VelafiStatus.PENDING
    assert order.tx_hash is None
    
    # Verify retry attempts
    assert monitor.service.get_order.call_count == monitor.max_retries + 1
    monitor.db.commit.assert_not_called()

@pytest.mark.asyncio
async def test_poll_pending_orders(monitor):
    """Test polling pending orders."""
    # Create test orders
    orders = [
        create_test_order(order_id="order1", status=VelafiStatus.PENDING),
        create_test_order(order_id="order2", status=VelafiStatus.PROCESSING)
    ]
    
    # Mock database query result
    mock_result = MagicMock()
    mock_result.scalars = MagicMock(return_value=MagicMock(all=lambda: orders))
    monitor.db.execute.return_value = mock_result
    
    # Mock VelaFi API responses
    monitor.service.get_order.side_effect = [
        {"status": "completed", "tx_hash": "0x1234..."},
        {"status": "failed"}
    ]
    
    # Poll pending orders
    await monitor.poll_pending_orders()
    
    # Verify API calls and database operations
    assert monitor.service.get_order.call_count == 2
    assert monitor.db.commit.call_count == 2
    
    # Verify order status updates
    assert orders[0].status == VelafiStatus.COMPLETED
    assert orders[0].tx_hash == "0x1234..."
    assert orders[1].status == VelafiStatus.FAILED
    assert orders[1].tx_hash is None