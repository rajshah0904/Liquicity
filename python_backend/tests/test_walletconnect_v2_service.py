"""
Tests for the WalletConnect v2 service
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import json
import qrcode
from io import BytesIO

from core.walletconnect_v2_service import (
    WalletConnectV2Service,
    WalletConnectSession,
    WalletConnectError,
    SessionStatus,
    ChainType
)

class TestWalletConnectV2Service:
    """Test WalletConnectV2Service class"""
    
    @pytest.fixture
    def wc_service(self):
        """Create a WalletConnect service for testing"""
        return WalletConnectV2Service(
            project_id="test_project_id",
            relay_url="relay.walletconnect.com",
            session_expiry_hours=24
        )
    
    @pytest.fixture
    def mock_session_data(self):
        """Create mock session data"""
        return {
            "id": "test_session_123",
            "user_id": "test_user_456",
            "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "chain_type": "evm",
            "chain_id": "ethereum",
            "status": "pending",
            "topic": "wc_test_session_123",
            "peer_metadata": {
                "name": "Test Wallet",
                "description": "Test wallet for development",
                "url": "https://testwallet.com",
                "icons": ["https://testwallet.com/icon.png"]
            },
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=24)
        }
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, wc_service):
        """Test service initialization"""
        assert wc_service.project_id == "test_project_id"
        assert wc_service.relay_url == "relay.walletconnect.com"
        assert wc_service.session_expiry_hours == 24
        assert wc_service.client is None
    
    @pytest.mark.asyncio
    async def test_get_client(self, wc_service):
        """Test getting WalletConnect client"""
        with patch('core.walletconnect_v2_service.WalletConnect') as mock_wc:
            mock_client = AsyncMock()
            mock_wc.return_value = mock_client
            
            client = await wc_service._get_client()
            
            assert client is not None
            mock_wc.assert_called_once_with(
                project_id="test_project_id",
                relay_url="relay.walletconnect.com"
            )
    
    @pytest.mark.asyncio
    async def test_create_session_success(self, wc_service):
        """Test successful session creation"""
        mock_client = AsyncMock()
        mock_client.create_session.return_value = {
            "topic": "wc_test_session_123",
            "uri": "wc:test_session_123@1?bridge=wss://relay.walletconnect.com&key=test_key"
        }
        
        with patch.object(wc_service, '_get_client', return_value=mock_client):
            with patch.object(wc_service, '_save_session', return_value=True):
                session = await wc_service.create_session(
                    user_id="test_user_456",
                    wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                    chain_type="evm",
                    chain_id="ethereum"
                )
                
                assert session.user_id == "test_user_456"
                assert session.wallet_address == "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
                assert session.chain_type == "evm"
                assert session.chain_id == "ethereum"
                assert session.status == "pending"
                assert session.topic == "wc_test_session_123"
    
    @pytest.mark.asyncio
    async def test_create_session_failure(self, wc_service):
        """Test session creation failure"""
        mock_client = AsyncMock()
        mock_client.create_session.side_effect = Exception("Failed to create session")
        
        with patch.object(wc_service, '_get_client', return_value=mock_client):
            with pytest.raises(WalletConnectError) as exc_info:
                await wc_service.create_session(
                    user_id="test_user_456",
                    wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                    chain_type="evm",
                    chain_id="ethereum"
                )
            
            assert "Failed to create session" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_qr_code_success(self, wc_service):
        """Test successful QR code generation"""
        session_uri = "wc:test_session_123@1?bridge=wss://relay.walletconnect.com&key=test_key"
        
        qr_code = wc_service.generate_qr_code(session_uri)
        
        assert qr_code.startswith("data:image/png;base64,")
        assert len(qr_code) > 100  # Should be a substantial base64 string
    
    @pytest.mark.asyncio
    async def test_generate_qr_code_invalid_uri(self, wc_service):
        """Test QR code generation with invalid URI"""
        with pytest.raises(ValueError) as exc_info:
            wc_service.generate_qr_code("")
        
        assert "Invalid session URI" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_session_status_success(self, wc_service, mock_session_data):
        """Test successful session status retrieval"""
        with patch.object(wc_service, '_get_session', return_value=mock_session_data):
            status = await wc_service.get_session_status("test_session_123")
            
            assert status["session_id"] == "test_session_123"
            assert status["user_id"] == "test_user_456"
            assert status["wallet_address"] == "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
            assert status["status"] == "pending"
            assert status["chain_type"] == "evm"
            assert status["chain_id"] == "ethereum"
    
    @pytest.mark.asyncio
    async def test_get_session_status_not_found(self, wc_service):
        """Test session status retrieval for non-existent session"""
        with patch.object(wc_service, '_get_session', return_value=None):
            with pytest.raises(WalletConnectError) as exc_info:
                await wc_service.get_session_status("non_existent_session")
            
            assert "Session not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_approve_session_success(self, wc_service, mock_session_data):
        """Test successful session approval"""
        mock_client = AsyncMock()
        mock_client.approve_session.return_value = True
        
        with patch.object(wc_service, '_get_client', return_value=mock_client):
            with patch.object(wc_service, '_get_session', return_value=mock_session_data):
                with patch.object(wc_service, '_update_session_status', return_value=True):
                    result = await wc_service.approve_session("test_session_123")
                    
                    assert result["success"] is True
                    assert result["session_id"] == "test_session_123"
                    assert result["status"] == "approved"
    
    @pytest.mark.asyncio
    async def test_reject_session_success(self, wc_service, mock_session_data):
        """Test successful session rejection"""
        mock_client = AsyncMock()
        mock_client.reject_session.return_value = True
        
        with patch.object(wc_service, '_get_client', return_value=mock_client):
            with patch.object(wc_service, '_get_session', return_value=mock_session_data):
                with patch.object(wc_service, '_update_session_status', return_value=True):
                    result = await wc_service.reject_session("test_session_123", "User rejected")
                    
                    assert result["success"] is True
                    assert result["session_id"] == "test_session_123"
                    assert result["status"] == "rejected"
                    assert result["reason"] == "User rejected"
    
    @pytest.mark.asyncio
    async def test_disconnect_session_success(self, wc_service, mock_session_data):
        """Test successful session disconnection"""
        mock_client = AsyncMock()
        mock_client.disconnect_session.return_value = True
        
        with patch.object(wc_service, '_get_client', return_value=mock_client):
            with patch.object(wc_service, '_get_session', return_value=mock_session_data):
                with patch.object(wc_service, '_update_session_status', return_value=True):
                    result = await wc_service.disconnect_session("test_session_123")
                    
                    assert result["success"] is True
                    assert result["session_id"] == "test_session_123"
                    assert result["status"] == "disconnected"
    
    @pytest.mark.asyncio
    async def test_send_transaction_request_success(self, wc_service, mock_session_data):
        """Test successful transaction request"""
        mock_client = AsyncMock()
        mock_client.send_transaction_request.return_value = {
            "request_id": "test_request_123",
            "status": "pending"
        }
        
        transaction_data = {
            "to": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "value": "1000000000000000000",  # 1 ETH in wei
            "data": "0x",
            "gas": "21000"
        }
        
        with patch.object(wc_service, '_get_client', return_value=mock_client):
            with patch.object(wc_service, '_get_session', return_value=mock_session_data):
                result = await wc_service.send_transaction_request(
                    "test_session_123",
                    transaction_data
                )
                
                assert result["request_id"] == "test_request_123"
                assert result["status"] == "pending"
    
    @pytest.mark.asyncio
    async def test_get_transaction_status_success(self, wc_service):
        """Test successful transaction status retrieval"""
        mock_client = AsyncMock()
        mock_client.get_transaction_status.return_value = {
            "request_id": "test_request_123",
            "status": "approved",
            "transaction_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        }
        
        with patch.object(wc_service, '_get_client', return_value=mock_client):
            result = await wc_service.get_transaction_status("test_request_123")
            
            assert result["request_id"] == "test_request_123"
            assert result["status"] == "approved"
            assert result["transaction_hash"] == "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(self, wc_service):
        """Test cleanup of expired sessions"""
        expired_sessions = [
            {
                "id": "expired_session_1",
                "expires_at": datetime.utcnow() - timedelta(hours=1)
            },
            {
                "id": "expired_session_2",
                "expires_at": datetime.utcnow() - timedelta(hours=2)
            }
        ]
        
        with patch.object(wc_service, '_get_expired_sessions', return_value=expired_sessions):
            with patch.object(wc_service, '_delete_session', return_value=True):
                result = await wc_service.cleanup_expired_sessions()
                
                assert result["cleaned_sessions"] == 2
                assert "expired_session_1" in result["deleted_sessions"]
                assert "expired_session_2" in result["deleted_sessions"]

class TestWalletConnectSession:
    """Test WalletConnectSession class"""
    
    def test_session_creation(self):
        """Test creating a WalletConnect session"""
        session = WalletConnectSession(
            id="test_session_123",
            user_id="test_user_456",
            wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            chain_type="evm",
            chain_id="ethereum",
            status="pending",
            topic="wc_test_session_123",
            peer_metadata={
                "name": "Test Wallet",
                "description": "Test wallet for development"
            },
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        assert session.id == "test_session_123"
        assert session.user_id == "test_user_456"
        assert session.wallet_address == "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
        assert session.chain_type == "evm"
        assert session.chain_id == "ethereum"
        assert session.status == "pending"
        assert session.topic == "wc_test_session_123"
        assert session.peer_metadata["name"] == "Test Wallet"
    
    def test_session_to_dict(self):
        """Test converting session to dictionary"""
        session = WalletConnectSession(
            id="test_session_123",
            user_id="test_user_456",
            wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            chain_type="evm",
            chain_id="ethereum",
            status="pending",
            topic="wc_test_session_123",
            peer_metadata={},
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        session_dict = session.to_dict()
        assert session_dict["id"] == "test_session_123"
        assert session_dict["user_id"] == "test_user_456"
        assert session_dict["wallet_address"] == "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
        assert session_dict["status"] == "pending"
    
    def test_session_is_expired(self):
        """Test session expiration check"""
        # Expired session
        expired_session = WalletConnectSession(
            id="expired_session",
            user_id="test_user",
            wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            chain_type="evm",
            chain_id="ethereum",
            status="pending",
            topic="wc_expired_session",
            peer_metadata={},
            created_at=datetime.utcnow() - timedelta(hours=25),
            expires_at=datetime.utcnow() - timedelta(hours=1)
        )
        
        assert expired_session.is_expired() is True
        
        # Active session
        active_session = WalletConnectSession(
            id="active_session",
            user_id="test_user",
            wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            chain_type="evm",
            chain_id="ethereum",
            status="pending",
            topic="wc_active_session",
            peer_metadata={},
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        assert active_session.is_expired() is False

class TestSessionStatus:
    """Test SessionStatus enum"""
    
    def test_session_status_values(self):
        """Test SessionStatus enum values"""
        assert SessionStatus.PENDING == "pending"
        assert SessionStatus.APPROVED == "approved"
        assert SessionStatus.REJECTED == "rejected"
        assert SessionStatus.DISCONNECTED == "disconnected"
        assert SessionStatus.EXPIRED == "expired"
    
    def test_session_status_validation(self):
        """Test SessionStatus validation"""
        assert SessionStatus.is_valid("pending") is True
        assert SessionStatus.is_valid("approved") is True
        assert SessionStatus.is_valid("rejected") is True
        assert SessionStatus.is_valid("disconnected") is True
        assert SessionStatus.is_valid("expired") is True
        assert SessionStatus.is_valid("invalid") is False

class TestChainType:
    """Test ChainType enum"""
    
    def test_chain_type_values(self):
        """Test ChainType enum values"""
        assert ChainType.EVM == "evm"
        assert ChainType.SOLANA == "solana"
    
    def test_chain_type_validation(self):
        """Test ChainType validation"""
        assert ChainType.is_valid("evm") is True
        assert ChainType.is_valid("solana") is True
        assert ChainType.is_valid("invalid") is False

class TestErrorHandling:
    """Test error handling"""
    
    @pytest.mark.asyncio
    async def test_walletconnect_error_creation(self):
        """Test WalletConnectError creation"""
        error = WalletConnectError("Test error message", error_code="TEST_ERROR")
        
        assert str(error) == "Test error message"
        assert error.error_code == "TEST_ERROR"
    
    @pytest.mark.asyncio
    async def test_session_not_found_error(self, wc_service):
        """Test handling of session not found error"""
        with patch.object(wc_service, '_get_session', return_value=None):
            with pytest.raises(WalletConnectError) as exc_info:
                await wc_service.get_session_status("non_existent_session")
            
            assert exc_info.value.error_code == "SESSION_NOT_FOUND"
    
    @pytest.mark.asyncio
    async def test_session_expired_error(self, wc_service):
        """Test handling of expired session error"""
        expired_session_data = {
            "id": "expired_session",
            "user_id": "test_user",
            "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "chain_type": "evm",
            "chain_id": "ethereum",
            "status": "pending",
            "topic": "wc_expired_session",
            "peer_metadata": {},
            "created_at": datetime.utcnow() - timedelta(hours=25),
            "expires_at": datetime.utcnow() - timedelta(hours=1)
        }
        
        with patch.object(wc_service, '_get_session', return_value=expired_session_data):
            with pytest.raises(WalletConnectError) as exc_info:
                await wc_service.get_session_status("expired_session")
            
            assert exc_info.value.error_code == "SESSION_EXPIRED"

class TestIntegration:
    """Test integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_complete_session_flow(self, wc_service):
        """Test complete session flow from creation to approval"""
        # Step 1: Create session
        mock_client = AsyncMock()
        mock_client.create_session.return_value = {
            "topic": "wc_test_session_123",
            "uri": "wc:test_session_123@1?bridge=wss://relay.walletconnect.com&key=test_key"
        }
        
        with patch.object(wc_service, '_get_client', return_value=mock_client):
            with patch.object(wc_service, '_save_session', return_value=True):
                session = await wc_service.create_session(
                    user_id="test_user_456",
                    wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                    chain_type="evm",
                    chain_id="ethereum"
                )
                
                assert session.status == "pending"
                
                # Step 2: Generate QR code
                qr_code = wc_service.generate_qr_code(session.uri)
                assert qr_code.startswith("data:image/png;base64,")
                
                # Step 3: Approve session
                mock_client.approve_session.return_value = True
                with patch.object(wc_service, '_update_session_status', return_value=True):
                    result = await wc_service.approve_session(session.id)
                    assert result["status"] == "approved"
    
    @pytest.mark.asyncio
    async def test_transaction_flow(self, wc_service):
        """Test complete transaction flow"""
        # Mock session data
        session_data = {
            "id": "test_session_123",
            "user_id": "test_user_456",
            "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "chain_type": "evm",
            "chain_id": "ethereum",
            "status": "approved",
            "topic": "wc_test_session_123",
            "peer_metadata": {},
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=24)
        }
        
        mock_client = AsyncMock()
        mock_client.send_transaction_request.return_value = {
            "request_id": "test_request_123",
            "status": "pending"
        }
        
        mock_client.get_transaction_status.return_value = {
            "request_id": "test_request_123",
            "status": "approved",
            "transaction_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        }
        
        transaction_data = {
            "to": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "value": "1000000000000000000",  # 1 ETH in wei
            "data": "0x",
            "gas": "21000"
        }
        
        with patch.object(wc_service, '_get_client', return_value=mock_client):
            with patch.object(wc_service, '_get_session', return_value=session_data):
                # Step 1: Send transaction request
                request_result = await wc_service.send_transaction_request(
                    "test_session_123",
                    transaction_data
                )
                
                assert request_result["request_id"] == "test_request_123"
                assert request_result["status"] == "pending"
                
                # Step 2: Check transaction status
                status_result = await wc_service.get_transaction_status("test_request_123")
                
                assert status_result["request_id"] == "test_request_123"
                assert status_result["status"] == "approved"
                assert status_result["transaction_hash"] == "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef" 