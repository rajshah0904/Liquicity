"""
Tests for the FastAPI routes
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import json

from fastapi_app import app
from core.security import SecurityContext
from core.bridge_api_client import BridgeTransfer
from core.usdc_payment_service import TransferResponse
from core.walletconnect_v2_service import WalletConnectSession

class TestAuthenticationRoutes:
    """Test authentication routes"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert "timestamp" in response.json()
    
    def test_login_success(self, client):
        """Test successful login"""
        login_data = {
            "email": "test@example.com",
            "password": "test_password"
        }
        
        mock_auth_result = {
            "success": True,
            "user_id": "test_user_123",
            "token": "test_jwt_token",
            "permissions": ["read", "write"]
        }
        
        with patch('api.routes.authenticate_user', return_value=mock_auth_result):
            response = client.post("/auth/login", json=login_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["user_id"] == "test_user_123"
            assert "token" in data
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        login_data = {
            "email": "test@example.com",
            "password": "wrong_password"
        }
        
        mock_auth_result = {
            "success": False,
            "error": "Invalid credentials"
        }
        
        with patch('api.routes.authenticate_user', return_value=mock_auth_result):
            response = client.post("/auth/login", json=login_data)
            
            assert response.status_code == 401
            data = response.json()
            assert data["success"] is False
            assert "Invalid credentials" in data["error"]
    
    def test_register_success(self, client):
        """Test successful user registration"""
        register_data = {
            "email": "newuser@example.com",
            "password": "new_password",
            "first_name": "John",
            "last_name": "Doe"
        }
        
        mock_register_result = {
            "success": True,
            "user_id": "new_user_123",
            "message": "User registered successfully"
        }
        
        with patch('api.routes.register_user', return_value=mock_register_result):
            response = client.post("/auth/register", json=register_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True
            assert data["user_id"] == "new_user_123"
    
    def test_register_existing_user(self, client):
        """Test registration with existing user"""
        register_data = {
            "email": "existing@example.com",
            "password": "password",
            "first_name": "John",
            "last_name": "Doe"
        }
        
        mock_register_result = {
            "success": False,
            "error": "User already exists"
        }
        
        with patch('api.routes.register_user', return_value=mock_register_result):
            response = client.post("/auth/register", json=register_data)
            
            assert response.status_code == 400
            data = response.json()
            assert data["success"] is False
            assert "User already exists" in data["error"]

class TestWalletConnectRoutes:
    """Test WalletConnect routes"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_auth_context(self):
        """Create mock authentication context"""
        return SecurityContext(
            user_id="test_user_123",
            ip_address="192.168.1.1",
            user_agent="test_agent",
            session_id="test_session_456",
            wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            risk_score=0.1,
            fraud_indicators=[],
            permissions=["read", "write"],
            last_activity=datetime.utcnow(),
            device_fingerprint="test_fingerprint"
        )
    
    def test_create_session_success(self, client, mock_auth_context):
        """Test successful session creation"""
        session_data = {
            "chain_type": "evm",
            "chain_id": "ethereum"
        }
        
        mock_session = WalletConnectSession(
            id="test_session_123",
            user_id="test_user_123",
            wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            chain_type="evm",
            chain_id="ethereum",
            status="pending",
            topic="wc_test_session_123",
            peer_metadata={},
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        with patch('api.routes.get_current_user', return_value=mock_auth_context):
            with patch('api.routes.walletconnect_service.create_session', return_value=mock_session):
                response = client.post("/walletconnect/session", json=session_data)
                
                assert response.status_code == 201
                data = response.json()
                assert data["success"] is True
                assert data["session_id"] == "test_session_123"
                assert data["status"] == "pending"
                assert "qr_code" in data
    
    def test_get_session_status_success(self, client, mock_auth_context):
        """Test successful session status retrieval"""
        mock_status = {
            "session_id": "test_session_123",
            "user_id": "test_user_123",
            "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "chain_type": "evm",
            "chain_id": "ethereum",
            "status": "approved",
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
        
        with patch('api.routes.get_current_user', return_value=mock_auth_context):
            with patch('api.routes.walletconnect_service.get_session_status', return_value=mock_status):
                response = client.get("/walletconnect/session/test_session_123")
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["session_id"] == "test_session_123"
                assert data["status"] == "approved"
    
    def test_approve_session_success(self, client, mock_auth_context):
        """Test successful session approval"""
        mock_result = {
            "success": True,
            "session_id": "test_session_123",
            "status": "approved"
        }
        
        with patch('api.routes.get_current_user', return_value=mock_auth_context):
            with patch('api.routes.walletconnect_service.approve_session', return_value=mock_result):
                response = client.post("/walletconnect/session/test_session_123/approve")
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["session_id"] == "test_session_123"
                assert data["status"] == "approved"
    
    def test_disconnect_session_success(self, client, mock_auth_context):
        """Test successful session disconnection"""
        mock_result = {
            "success": True,
            "session_id": "test_session_123",
            "status": "disconnected"
        }
        
        with patch('api.routes.get_current_user', return_value=mock_auth_context):
            with patch('api.routes.walletconnect_service.disconnect_session', return_value=mock_result):
                response = client.delete("/walletconnect/session/test_session_123")
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["session_id"] == "test_session_123"
                assert data["status"] == "disconnected"

class TestTransferRoutes:
    """Test transfer routes"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_auth_context(self):
        """Create mock authentication context"""
        return SecurityContext(
            user_id="test_user_123",
            ip_address="192.168.1.1",
            user_agent="test_agent",
            session_id="test_session_456",
            wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            risk_score=0.1,
            fraud_indicators=[],
            permissions=["read", "write", "transfer"],
            last_activity=datetime.utcnow(),
            device_fingerprint="test_fingerprint"
        )
    
    def test_create_transfer_success(self, client, mock_auth_context):
        """Test successful transfer creation"""
        transfer_data = {
            "amount": "100.00",
            "source_network": "ethereum",
            "source_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "destination_network": "polygon",
            "destination_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "currency": "usdc",
            "urgency": "low",
            "metadata": {"user_id": "test_user_123"}
        }
        
        mock_transfer = BridgeTransfer(
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
        
        with patch('api.routes.get_current_user', return_value=mock_auth_context):
            with patch('api.routes.bridge_client.create_transfer', return_value=mock_transfer):
                response = client.post("/transfers", json=transfer_data)
                
                assert response.status_code == 201
                data = response.json()
                assert data["success"] is True
                assert data["transfer_id"] == "test_transfer_123"
                assert data["status"] == "pending"
                assert data["amount"] == "100.00"
    
    def test_create_transfer_insufficient_permissions(self, client):
        """Test transfer creation with insufficient permissions"""
        mock_auth_context = SecurityContext(
            user_id="test_user_123",
            ip_address="192.168.1.1",
            user_agent="test_agent",
            session_id="test_session_456",
            wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            risk_score=0.1,
            fraud_indicators=[],
            permissions=["read"],  # No transfer permission
            last_activity=datetime.utcnow(),
            device_fingerprint="test_fingerprint"
        )
        
        transfer_data = {
            "amount": "100.00",
            "source_network": "ethereum",
            "source_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "destination_network": "polygon",
            "destination_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "currency": "usdc",
            "urgency": "low"
        }
        
        with patch('api.routes.get_current_user', return_value=mock_auth_context):
            response = client.post("/transfers", json=transfer_data)
            
            assert response.status_code == 403
            data = response.json()
            assert data["success"] is False
            assert "Insufficient permissions" in data["error"]
    
    def test_get_transfer_status_success(self, client, mock_auth_context):
        """Test successful transfer status retrieval"""
        mock_transfer = BridgeTransfer(
            transfer_id="test_transfer_123",
            status="completed",
            amount="100.00",
            source_network="ethereum",
            destination_network="polygon",
            estimated_fee="2.50",
            estimated_time=300,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=1),
            transaction_hash="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        )
        
        with patch('api.routes.get_current_user', return_value=mock_auth_context):
            with patch('api.routes.bridge_client.get_transfer_status', return_value=mock_transfer):
                response = client.get("/transfers/test_transfer_123")
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["transfer_id"] == "test_transfer_123"
                assert data["status"] == "completed"
                assert "transaction_hash" in data
    
    def test_estimate_fee_success(self, client, mock_auth_context):
        """Test successful fee estimation"""
        fee_data = {
            "amount": "100.00",
            "source_network": "ethereum",
            "destination_network": "polygon",
            "currency": "usdc",
            "urgency": "low"
        }
        
        mock_fee_estimate = {
            "fee": "2.50",
            "currency": "usdc",
            "estimated_time": 300,
            "breakdown": {
                "bridge_fee": "1.00",
                "gas_fee": "1.50"
            }
        }
        
        with patch('api.routes.get_current_user', return_value=mock_auth_context):
            with patch('api.routes.bridge_client.estimate_fee', return_value=mock_fee_estimate):
                response = client.post("/transfers/estimate-fee", json=fee_data)
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["fee"] == "2.50"
                assert data["currency"] == "usdc"
                assert data["estimated_time"] == 300
                assert "breakdown" in data
    
    def test_get_transfer_history_success(self, client, mock_auth_context):
        """Test successful transfer history retrieval"""
        mock_history = {
            "transfers": [
                {
                    "transfer_id": "test_transfer_1",
                    "status": "completed",
                    "amount": "100.00",
                    "created_at": datetime.utcnow().isoformat()
                },
                {
                    "transfer_id": "test_transfer_2",
                    "status": "pending",
                    "amount": "50.00",
                    "created_at": datetime.utcnow().isoformat()
                }
            ],
            "pagination": {
                "page": 1,
                "limit": 10,
                "total": 2
            }
        }
        
        with patch('api.routes.get_current_user', return_value=mock_auth_context):
            with patch('api.routes.bridge_client.get_transfer_history', return_value=mock_history):
                response = client.get("/transfers/history?page=1&limit=10")
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert len(data["transfers"]) == 2
                assert data["pagination"]["total"] == 2

class TestUSDCRoutes:
    """Test USDC payment routes"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_auth_context(self):
        """Create mock authentication context"""
        return SecurityContext(
            user_id="test_user_123",
            ip_address="192.168.1.1",
            user_agent="test_agent",
            session_id="test_session_456",
            wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            risk_score=0.1,
            fraud_indicators=[],
            permissions=["read", "write", "transfer"],
            last_activity=datetime.utcnow(),
            device_fingerprint="test_fingerprint"
        )
    
    def test_create_usdc_transfer_success(self, client, mock_auth_context):
        """Test successful USDC transfer creation"""
        transfer_data = {
            "session_id": "test_session_123",
            "from_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "to_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "amount": "100.00",
            "chain_type": "evm",
            "chain_id": "ethereum",
            "currency": "usdc",
            "urgency": "low",
            "metadata": {"user_id": "test_user_123"}
        }
        
        mock_transfer = TransferResponse(
            id="test_transfer_456",
            session_id="test_session_123",
            from_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            to_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            amount="100.00",
            chain_type="evm",
            chain_id="ethereum",
            currency="usdc",
            status="pending",
            transaction_hash="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            gas_estimate=MagicMock(
                gas_price="20000000000",
                gas_limit=65000,
                total_cost="0.0013",
                estimated_time=60
            ),
            created_at=datetime.utcnow()
        )
        
        with patch('api.routes.get_current_user', return_value=mock_auth_context):
            with patch('api.routes.usdc_service.create_usdc_transfer', return_value=mock_transfer):
                response = client.post("/usdc/transfer", json=transfer_data)
                
                assert response.status_code == 201
                data = response.json()
                assert data["success"] is True
                assert data["transfer_id"] == "test_transfer_456"
                assert data["status"] == "pending"
                assert data["amount"] == "100.00"
    
    def test_estimate_gas_success(self, client, mock_auth_context):
        """Test successful gas estimation"""
        gas_data = {
            "chain_id": "ethereum",
            "from_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "to_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "amount": "100.00"
        }
        
        mock_gas_estimate = MagicMock(
            gas_price="20000000000",
            gas_limit=65000,
            total_cost="0.0013",
            estimated_time=60,
            max_priority_fee=None
        )
        
        with patch('api.routes.get_current_user', return_value=mock_auth_context):
            with patch('api.routes.usdc_service._estimate_gas', return_value=mock_gas_estimate):
                response = client.post("/usdc/estimate-gas", json=gas_data)
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["gas_price"] == "20000000000"
                assert data["gas_limit"] == 65000
                assert data["total_cost"] == "0.0013"
                assert data["estimated_time"] == 60

class TestErrorHandling:
    """Test error handling in routes"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_invalid_json_request(self, client):
        """Test handling of invalid JSON requests"""
        response = client.post("/auth/login", data="invalid json")
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        """Test handling of missing required fields"""
        login_data = {
            "email": "test@example.com"
            # Missing password
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 422
    
    def test_invalid_network_parameter(self, client):
        """Test handling of invalid network parameters"""
        transfer_data = {
            "amount": "100.00",
            "source_network": "invalid_network",  # Invalid network
            "source_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "destination_network": "polygon",
            "destination_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "currency": "usdc",
            "urgency": "low"
        }
        
        response = client.post("/transfers", json=transfer_data)
        assert response.status_code == 422
    
    def test_invalid_amount_format(self, client):
        """Test handling of invalid amount format"""
        transfer_data = {
            "amount": "invalid_amount",  # Invalid amount
            "source_network": "ethereum",
            "source_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "destination_network": "polygon",
            "destination_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "currency": "usdc",
            "urgency": "low"
        }
        
        response = client.post("/transfers", json=transfer_data)
        assert response.status_code == 422
    
    def test_unauthorized_access(self, client):
        """Test handling of unauthorized access"""
        # Try to access protected endpoint without authentication
        response = client.get("/transfers/history")
        assert response.status_code == 401
    
    def test_invalid_session_id(self, client):
        """Test handling of invalid session ID"""
        response = client.get("/walletconnect/session/invalid_session_id")
        assert response.status_code == 401  # No authentication
    
    def test_invalid_transfer_id(self, client):
        """Test handling of invalid transfer ID"""
        response = client.get("/transfers/invalid_transfer_id")
        assert response.status_code == 401  # No authentication

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_rate_limiting_exceeded(self, client):
        """Test rate limiting when exceeded"""
        # Make multiple rapid requests to trigger rate limiting
        for _ in range(100):  # Exceed rate limit
            response = client.get("/health")
        
        # The last request should be rate limited
        assert response.status_code == 429
        data = response.json()
        assert "rate limit" in data["error"].lower()

class TestValidation:
    """Test input validation"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_email_validation(self, client):
        """Test email format validation"""
        register_data = {
            "email": "invalid_email",  # Invalid email format
            "password": "password",
            "first_name": "John",
            "last_name": "Doe"
        }
        
        response = client.post("/auth/register", json=register_data)
        assert response.status_code == 422
    
    def test_password_validation(self, client):
        """Test password strength validation"""
        register_data = {
            "email": "test@example.com",
            "password": "123",  # Too short
            "first_name": "John",
            "last_name": "Doe"
        }
        
        response = client.post("/auth/register", json=register_data)
        assert response.status_code == 422
    
    def test_wallet_address_validation(self, client):
        """Test wallet address format validation"""
        transfer_data = {
            "amount": "100.00",
            "source_network": "ethereum",
            "source_address": "invalid_address",  # Invalid address
            "destination_network": "polygon",
            "destination_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "currency": "usdc",
            "urgency": "low"
        }
        
        response = client.post("/transfers", json=transfer_data)
        assert response.status_code == 422 