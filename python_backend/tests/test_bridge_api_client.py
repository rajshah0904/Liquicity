"""
Tests for the Bridge API client
"""

import pytest
import aiohttp
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import json

from core.bridge_api_client import (
    BridgeAPIClient,
    PaymentRail,
    TransferStatus,
    BridgeTransfer,
    BridgeError,
    NetworkConfig
)

class TestBridgeAPIClient:
    """Test BridgeAPIClient class"""
    
    @pytest.fixture
    def bridge_client(self):
        """Create a Bridge API client for testing"""
        return BridgeAPIClient(
            api_key="test_api_key",
            base_url="https://api.bridge.xyz",
            timeout=30
        )
    
    @pytest.mark.asyncio
    async def test_client_initialization(self, bridge_client):
        """Test client initialization"""
        assert bridge_client.api_key == "test_api_key"
        assert bridge_client.base_url == "https://api.bridge.xyz"
        assert bridge_client.timeout == 30
        assert bridge_client.session is None
    
    @pytest.mark.asyncio
    async def test_get_session(self, bridge_client):
        """Test getting aiohttp session"""
        session = await bridge_client._get_session()
        assert isinstance(session, aiohttp.ClientSession)
        
        # Should reuse the same session
        session2 = await bridge_client._get_session()
        assert session is session2
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, bridge_client):
        """Test successful API request"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {"test": "data"}
        }
        
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        with patch.object(bridge_client, '_get_session', return_value=mock_session):
            result = await bridge_client._make_request(
                "POST", "/test", {"test": "data"}
            )
            
            assert result["success"] is True
            assert result["data"]["test"] == "data"
    
    @pytest.mark.asyncio
    async def test_make_request_error(self, bridge_client):
        """Test API request with error"""
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.json.return_value = {
            "success": False,
            "error": "Bad Request"
        }
        
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        with patch.object(bridge_client, '_get_session', return_value=mock_session):
            with pytest.raises(BridgeError) as exc_info:
                await bridge_client._make_request("POST", "/test", {})
            
            assert "Bad Request" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_transfer_success(self, bridge_client):
        """Test successful transfer creation"""
        mock_response = {
            "success": True,
            "data": {
                "transfer_id": "test_transfer_123",
                "status": "pending",
                "amount": "100.00",
                "source_network": "ethereum",
                "destination_network": "polygon",
                "estimated_fee": "2.50",
                "estimated_time": 300,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
            }
        }
        
        with patch.object(bridge_client, '_make_request', return_value=mock_response):
            transfer = await bridge_client.create_transfer(
                amount="100.00",
                source_network="ethereum",
                source_address="0x1234567890abcdef",
                destination_network="polygon",
                destination_address="0xfedcba0987654321",
                currency="usdc",
                urgency="low",
                metadata={"user_id": "test_user"}
            )
            
            assert transfer.transfer_id == "test_transfer_123"
            assert transfer.status == "pending"
            assert transfer.amount == "100.00"
            assert transfer.source_network == "ethereum"
            assert transfer.destination_network == "polygon"
    
    @pytest.mark.asyncio
    async def test_get_transfer_status_success(self, bridge_client):
        """Test successful transfer status retrieval"""
        mock_response = {
            "success": True,
            "data": {
                "transfer_id": "test_transfer_123",
                "status": "completed",
                "amount": "100.00",
                "source_network": "ethereum",
                "destination_network": "polygon",
                "estimated_fee": "2.50",
                "estimated_time": 300,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                "transaction_hash": "0x1234567890abcdef"
            }
        }
        
        with patch.object(bridge_client, '_make_request', return_value=mock_response):
            transfer = await bridge_client.get_transfer_status("test_transfer_123")
            
            assert transfer.transfer_id == "test_transfer_123"
            assert transfer.status == "completed"
            assert transfer.transaction_hash == "0x1234567890abcdef"
    
    @pytest.mark.asyncio
    async def test_estimate_fee_success(self, bridge_client):
        """Test successful fee estimation"""
        mock_response = {
            "success": True,
            "data": {
                "fee": "2.50",
                "currency": "usdc",
                "estimated_time": 300,
                "breakdown": {
                    "bridge_fee": "1.00",
                    "gas_fee": "1.50"
                }
            }
        }
        
        with patch.object(bridge_client, '_make_request', return_value=mock_response):
            fee_estimate = await bridge_client.estimate_fee(
                amount="100.00",
                source_network="ethereum",
                destination_network="polygon",
                currency="usdc",
                urgency="low"
            )
            
            assert fee_estimate["fee"] == "2.50"
            assert fee_estimate["currency"] == "usdc"
            assert fee_estimate["estimated_time"] == 300
            assert "breakdown" in fee_estimate
    
    @pytest.mark.asyncio
    async def test_get_supported_networks(self, bridge_client):
        """Test getting supported networks"""
        mock_response = {
            "success": True,
            "data": {
                "networks": [
                    {
                        "id": "ethereum",
                        "name": "Ethereum",
                        "type": "evm",
                        "chain_id": 1,
                        "currency": "eth",
                        "status": "active"
                    },
                    {
                        "id": "polygon",
                        "name": "Polygon",
                        "type": "evm",
                        "chain_id": 137,
                        "currency": "matic",
                        "status": "active"
                    }
                ]
            }
        }
        
        with patch.object(bridge_client, '_make_request', return_value=mock_response):
            networks = await bridge_client.get_supported_networks()
            
            assert len(networks) == 2
            assert networks[0]["id"] == "ethereum"
            assert networks[1]["id"] == "polygon"
    
    @pytest.mark.asyncio
    async def test_get_network_config(self, bridge_client):
        """Test getting network configuration"""
        mock_response = {
            "success": True,
            "data": {
                "id": "ethereum",
                "name": "Ethereum",
                "type": "evm",
                "chain_id": 1,
                "currency": "eth",
                "status": "active",
                "config": {
                    "rpc_url": "https://eth-mainnet.alchemyapi.io/v2/...",
                    "contract_address": "0x1234567890abcdef",
                    "min_amount": "0.001",
                    "max_amount": "10000"
                }
            }
        }
        
        with patch.object(bridge_client, '_make_request', return_value=mock_response):
            config = await bridge_client.get_network_config("ethereum")
            
            assert config["id"] == "ethereum"
            assert config["type"] == "evm"
            assert config["chain_id"] == 1
            assert "config" in config
    
    @pytest.mark.asyncio
    async def test_cancel_transfer_success(self, bridge_client):
        """Test successful transfer cancellation"""
        mock_response = {
            "success": True,
            "data": {
                "transfer_id": "test_transfer_123",
                "status": "cancelled",
                "cancelled_at": datetime.utcnow().isoformat()
            }
        }
        
        with patch.object(bridge_client, '_make_request', return_value=mock_response):
            result = await bridge_client.cancel_transfer("test_transfer_123")
            
            assert result["transfer_id"] == "test_transfer_123"
            assert result["status"] == "cancelled"
    
    @pytest.mark.asyncio
    async def test_get_transfer_history(self, bridge_client):
        """Test getting transfer history"""
        mock_response = {
            "success": True,
            "data": {
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
        }
        
        with patch.object(bridge_client, '_make_request', return_value=mock_response):
            history = await bridge_client.get_transfer_history(
                user_id="test_user",
                page=1,
                limit=10
            )
            
            assert len(history["transfers"]) == 2
            assert history["pagination"]["total"] == 2

class TestPaymentRail:
    """Test PaymentRail enum"""
    
    def test_payment_rail_values(self):
        """Test PaymentRail enum values"""
        assert PaymentRail.ETHEREUM == "ethereum"
        assert PaymentRail.POLYGON == "polygon"
        assert PaymentRail.BASE == "base"
        assert PaymentRail.SOLANA == "solana"
    
    def test_payment_rail_validation(self):
        """Test PaymentRail validation"""
        assert PaymentRail.is_valid("ethereum") is True
        assert PaymentRail.is_valid("polygon") is True
        assert PaymentRail.is_valid("invalid") is False

class TestTransferStatus:
    """Test TransferStatus enum"""
    
    def test_transfer_status_values(self):
        """Test TransferStatus enum values"""
        assert TransferStatus.PENDING == "pending"
        assert TransferStatus.PROCESSING == "processing"
        assert TransferStatus.COMPLETED == "completed"
        assert TransferStatus.FAILED == "failed"
        assert TransferStatus.CANCELLED == "cancelled"
    
    def test_transfer_status_validation(self):
        """Test TransferStatus validation"""
        assert TransferStatus.is_valid("pending") is True
        assert TransferStatus.is_valid("completed") is True
        assert TransferStatus.is_valid("invalid") is False

class TestBridgeTransfer:
    """Test BridgeTransfer class"""
    
    def test_bridge_transfer_creation(self):
        """Test creating a BridgeTransfer"""
        transfer = BridgeTransfer(
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
        
        assert transfer.transfer_id == "test_transfer_123"
        assert transfer.status == "pending"
        assert transfer.amount == "100.00"
        assert transfer.source_network == "ethereum"
        assert transfer.destination_network == "polygon"
    
    def test_bridge_transfer_to_dict(self):
        """Test converting BridgeTransfer to dictionary"""
        transfer = BridgeTransfer(
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
        
        transfer_dict = transfer.to_dict()
        assert transfer_dict["transfer_id"] == "test_transfer_123"
        assert transfer_dict["status"] == "pending"
        assert transfer_dict["amount"] == "100.00"

class TestNetworkConfig:
    """Test NetworkConfig class"""
    
    def test_network_config_creation(self):
        """Test creating a NetworkConfig"""
        config = NetworkConfig(
            network_id="ethereum",
            name="Ethereum",
            type="evm",
            chain_id=1,
            currency="eth",
            status="active",
            rpc_url="https://eth-mainnet.alchemyapi.io/v2/...",
            contract_address="0x1234567890abcdef",
            min_amount="0.001",
            max_amount="10000"
        )
        
        assert config.network_id == "ethereum"
        assert config.name == "Ethereum"
        assert config.type == "evm"
        assert config.chain_id == 1
        assert config.currency == "eth"
        assert config.status == "active"
    
    def test_network_config_validation(self):
        """Test NetworkConfig validation"""
        config = NetworkConfig(
            network_id="ethereum",
            name="Ethereum",
            type="evm",
            chain_id=1,
            currency="eth",
            status="active",
            rpc_url="https://eth-mainnet.alchemyapi.io/v2/...",
            contract_address="0x1234567890abcdef",
            min_amount="0.001",
            max_amount="10000"
        )
        
        assert config.is_valid() is True
        
        # Invalid chain ID
        config.chain_id = -1
        assert config.is_valid() is False

class TestErrorHandling:
    """Test error handling"""
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self, bridge_client):
        """Test handling of network errors"""
        mock_session = AsyncMock()
        mock_session.post.side_effect = aiohttp.ClientError("Network error")
        
        with patch.object(bridge_client, '_get_session', return_value=mock_session):
            with pytest.raises(BridgeError) as exc_info:
                await bridge_client.create_transfer(
                    amount="100.00",
                    source_network="ethereum",
                    source_address="0x1234567890abcdef",
                    destination_network="polygon",
                    destination_address="0xfedcba0987654321",
                    currency="usdc"
                )
            
            assert "Network error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_timeout_error_handling(self, bridge_client):
        """Test handling of timeout errors"""
        mock_session = AsyncMock()
        mock_session.post.side_effect = asyncio.TimeoutError("Request timeout")
        
        with patch.object(bridge_client, '_get_session', return_value=mock_session):
            with pytest.raises(BridgeError) as exc_info:
                await bridge_client.create_transfer(
                    amount="100.00",
                    source_network="ethereum",
                    source_address="0x1234567890abcdef",
                    destination_network="polygon",
                    destination_address="0xfedcba0987654321",
                    currency="usdc"
                )
            
            assert "timeout" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_invalid_response_handling(self, bridge_client):
        """Test handling of invalid responses"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        with patch.object(bridge_client, '_get_session', return_value=mock_session):
            with pytest.raises(BridgeError) as exc_info:
                await bridge_client.create_transfer(
                    amount="100.00",
                    source_network="ethereum",
                    source_address="0x1234567890abcdef",
                    destination_network="polygon",
                    destination_address="0xfedcba0987654321",
                    currency="usdc"
                )
            
            assert "Invalid response" in str(exc_info.value)

class TestRetryLogic:
    """Test retry logic"""
    
    @pytest.mark.asyncio
    async def test_retry_on_failure(self, bridge_client):
        """Test retry logic on API failures"""
        # First call fails, second succeeds
        mock_response1 = AsyncMock()
        mock_response1.status = 500
        
        mock_response2 = AsyncMock()
        mock_response2.status = 200
        mock_response2.json.return_value = {
            "success": True,
            "data": {"transfer_id": "test_transfer_123"}
        }
        
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.side_effect = [mock_response1, mock_response2]
        
        with patch.object(bridge_client, '_get_session', return_value=mock_session):
            # This should retry and eventually succeed
            result = await bridge_client._make_request("POST", "/test", {})
            assert result["success"] is True
            assert result["data"]["transfer_id"] == "test_transfer_123"
    
    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, bridge_client):
        """Test when max retries are exceeded"""
        mock_response = AsyncMock()
        mock_response.status = 500
        
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        with patch.object(bridge_client, '_get_session', return_value=mock_session):
            with pytest.raises(BridgeError) as exc_info:
                await bridge_client._make_request("POST", "/test", {})
            
            assert "Max retries exceeded" in str(exc_info.value) 