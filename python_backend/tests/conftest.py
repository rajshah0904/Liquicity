"""
Pytest configuration and fixtures for testing the Python backend
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
import aiohttp
from fastapi.testclient import TestClient

# Import your FastAPI app
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi_app import app
from core.security import SecurityContext, BridgeTransferRequest
from core.bridge_api_client import BridgeAPIClient, PaymentRail
from core.usdc_payment_service import USDCPaymentService
from core.walletconnect_v2_service import WalletConnectV2Service

@pytest.fixture
def test_client():
    """FastAPI test client"""
    return TestClient(app)

@pytest.fixture
def mock_security_context():
    """Mock security context for testing"""
    return SecurityContext(
        user_id="test_user_123",
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        session_id="test_session_456",
        wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
        risk_score=0.1,
        fraud_indicators=[],
        permissions=["read", "write"],
        last_activity=datetime.utcnow(),
        device_fingerprint="test_fingerprint_789"
    )

@pytest.fixture
def mock_bridge_transfer_request():
    """Mock bridge transfer request for testing"""
    return BridgeTransferRequest(
        amount="100.00",
        source_network="ethereum",
        source_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
        destination_network="polygon",
        destination_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
        currency="usdc",
        urgency="low",
        metadata={"user_id": "test_user_123", "test": True}
    )

@pytest.fixture
def mock_bridge_client():
    """Mock Bridge API client"""
    client = AsyncMock(spec=BridgeAPIClient)
    client.api_key = "test_api_key"
    client.base_url = "https://api.bridge.xyz"
    
    # Mock successful responses
    client.create_transfer.return_value = AsyncMock(
        transfer_id="test_transfer_123",
        status="pending",
        amount="100.00",
        source_network="ethereum",
        destination_network="polygon",
        estimated_fee="2.50",
        estimated_time=300,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    
    client.get_transfer_status.return_value = AsyncMock(
        transfer_id="test_transfer_123",
        status="completed",
        amount="100.00",
        source_network="ethereum",
        destination_network="polygon",
        estimated_fee="2.50",
        estimated_time=300,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=1),
        transaction_hash="0x1234567890abcdef"
    )
    
    client.estimate_fee.return_value = {
        "fee": "2.50",
        "currency": "usdc",
        "estimated_time": 300
    }
    
    return client

@pytest.fixture
def mock_usdc_service():
    """Mock USDC payment service"""
    service = AsyncMock(spec=USDCPaymentService)
    
    # Mock transfer creation
    service.create_usdc_transfer.return_value = AsyncMock(
        id="test_transfer_456",
        session_id="test_session_789",
        from_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
        to_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
        amount="100.00",
        chain_type="evm",
        chain_id="ethereum",
        currency="usdc",
        status="pending",
        created_at=datetime.utcnow()
    )
    
    # Mock gas estimation
    service._estimate_evm_gas.return_value = AsyncMock(
        gas_price="20000000000",  # 20 Gwei
        gas_limit=65000,
        total_cost="0.0013",
        estimated_time=60,
        max_priority_fee=None
    )
    
    return service

@pytest.fixture
def mock_walletconnect_service():
    """Mock WalletConnect service"""
    service = AsyncMock(spec=WalletConnectV2Service)
    
    # Mock session creation
    service.create_session.return_value = AsyncMock(
        id="test_session_123",
        user_id="test_user_456",
        wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
        chain_type="evm",
        chain_id="ethereum",
        status="pending",
        topic="wc_test_session_123",
        peer_metadata={},
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    
    # Mock QR code generation
    service.generate_qr_code.return_value = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    # Mock session status
    service.get_session_status.return_value = {
        "session_id": "test_session_123",
        "user_id": "test_user_456",
        "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
        "chain_type": "evm",
        "chain_id": "ethereum",
        "status": "approved",
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
    }
    
    return service

@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp session for testing"""
    session = AsyncMock(spec=aiohttp.ClientSession)
    
    # Mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {
        "success": True,
        "data": {"test": "data"}
    }
    mock_response.text.return_value = '{"success": true, "data": {"test": "data"}}'
    
    session.request.return_value.__aenter__.return_value = mock_response
    session.post.return_value.__aenter__.return_value = mock_response
    session.get.return_value.__aenter__.return_value = mock_response
    
    return session

@pytest.fixture
def test_settings():
    """Test settings configuration"""
    return {
        "bridge_api_key": "test_bridge_api_key",
        "bridge_base_url": "https://api.bridge.xyz",
        "walletconnect_project_id": "test_project_id",
        "walletconnect_relay_url": "relay.walletconnect.com",
        "session_expiry_hours": 24,
        "supported_networks": ["ethereum", "polygon", "base", "solana"],
        "max_transaction_amount": "10000",
        "min_transaction_amount": "1"
    }

# Async test support
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close() 