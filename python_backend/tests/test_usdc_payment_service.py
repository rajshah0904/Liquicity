"""
Tests for the USDC payment service
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import json
from decimal import Decimal

from core.usdc_payment_service import (
    USDCPaymentService,
    TransferRequest,
    TransferResponse,
    GasEstimate,
    TransactionStatus,
    ChainType,
    NetworkConfig
)

class TestUSDCPaymentService:
    """Test USDCPaymentService class"""
    
    @pytest.fixture
    def usdc_service(self):
        """Create a USDC payment service for testing"""
        return USDCPaymentService(
            ethereum_rpc_url="https://eth-mainnet.alchemyapi.io/v2/test",
            polygon_rpc_url="https://polygon-rpc.com",
            base_rpc_url="https://mainnet.base.org",
            solana_rpc_url="https://api.mainnet-beta.solana.com"
        )
    
    @pytest.fixture
    def transfer_request(self):
        """Create a transfer request for testing"""
        return TransferRequest(
            session_id="test_session_123",
            from_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            to_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            amount="100.00",
            chain_type="evm",
            chain_id="ethereum",
            currency="usdc",
            urgency="low",
            metadata={"user_id": "test_user"}
        )
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, usdc_service):
        """Test service initialization"""
        assert usdc_service.ethereum_rpc_url == "https://eth-mainnet.alchemyapi.io/v2/test"
        assert usdc_service.polygon_rpc_url == "https://polygon-rpc.com"
        assert usdc_service.base_rpc_url == "https://mainnet.base.org"
        assert usdc_service.solana_rpc_url == "https://api.mainnet-beta.solana.com"
        assert usdc_service.session is None
    
    @pytest.mark.asyncio
    async def test_get_session(self, usdc_service):
        """Test getting aiohttp session"""
        session = await usdc_service._get_session()
        assert session is not None
        
        # Should reuse the same session
        session2 = await usdc_service._get_session()
        assert session is session2
    
    @pytest.mark.asyncio
    async def test_create_usdc_transfer_success(self, usdc_service, transfer_request):
        """Test successful USDC transfer creation"""
        with patch.object(usdc_service, '_validate_transfer_request', return_value=True):
            with patch.object(usdc_service, '_estimate_gas', return_value=AsyncMock(
                gas_price="20000000000",
                gas_limit=65000,
                total_cost="0.0013",
                estimated_time=60
            )):
                transfer = await usdc_service.create_usdc_transfer(transfer_request)
                
                assert transfer.session_id == "test_session_123"
                assert transfer.from_address == "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
                assert transfer.to_address == "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
                assert transfer.amount == "100.00"
                assert transfer.chain_type == "evm"
                assert transfer.chain_id == "ethereum"
                assert transfer.currency == "usdc"
                assert transfer.status == "pending"
    
    @pytest.mark.asyncio
    async def test_create_usdc_transfer_validation_failure(self, usdc_service, transfer_request):
        """Test transfer creation with validation failure"""
        with patch.object(usdc_service, '_validate_transfer_request', return_value=False):
            with pytest.raises(ValueError) as exc_info:
                await usdc_service.create_usdc_transfer(transfer_request)
            
            assert "Invalid transfer request" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_estimate_gas_ethereum(self, usdc_service):
        """Test gas estimation for Ethereum"""
        mock_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "gasPrice": "0x4a817c800",  # 20 Gwei
                "gasLimit": "0x186a0"  # 100,000
            }
        }
        
        mock_session = AsyncMock()
        mock_response_obj = AsyncMock()
        mock_response_obj.json.return_value = mock_response
        mock_session.post.return_value.__aenter__.return_value = mock_response_obj
        
        with patch.object(usdc_service, '_get_session', return_value=mock_session):
            gas_estimate = await usdc_service._estimate_evm_gas(
                chain_id="ethereum",
                from_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                to_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                amount="100.00"
            )
            
            assert gas_estimate.gas_price == "20000000000"
            assert gas_estimate.gas_limit == 100000
            assert isinstance(gas_estimate.total_cost, str)
            assert gas_estimate.estimated_time == 60
    
    @pytest.mark.asyncio
    async def test_estimate_gas_polygon(self, usdc_service):
        """Test gas estimation for Polygon"""
        mock_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "gasPrice": "0x3b9aca00",  # 1 Gwei
                "gasLimit": "0x186a0"  # 100,000
            }
        }
        
        mock_session = AsyncMock()
        mock_response_obj = AsyncMock()
        mock_response_obj.json.return_value = mock_response
        mock_session.post.return_value.__aenter__.return_value = mock_response_obj
        
        with patch.object(usdc_service, '_get_session', return_value=mock_session):
            gas_estimate = await usdc_service._estimate_evm_gas(
                chain_id="polygon",
                from_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                to_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                amount="100.00"
            )
            
            assert gas_estimate.gas_price == "1000000000"
            assert gas_estimate.gas_limit == 100000
            assert isinstance(gas_estimate.total_cost, str)
            assert gas_estimate.estimated_time == 30  # Polygon is faster
    
    @pytest.mark.asyncio
    async def test_estimate_gas_solana(self, usdc_service):
        """Test gas estimation for Solana"""
        mock_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "value": {
                    "feeCalculator": {
                        "lamportsPerSignature": 5000
                    }
                }
            }
        }
        
        mock_session = AsyncMock()
        mock_response_obj = AsyncMock()
        mock_response_obj.json.return_value = mock_response
        mock_session.post.return_value.__aenter__.return_value = mock_response_obj
        
        with patch.object(usdc_service, '_get_session', return_value=mock_session):
            gas_estimate = await usdc_service._estimate_solana_gas(
                from_address="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
                to_address="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
                amount="100.00"
            )
            
            assert gas_estimate.gas_price == "5000"
            assert gas_estimate.gas_limit == 1  # Solana uses 1 transaction
            assert isinstance(gas_estimate.total_cost, str)
            assert gas_estimate.estimated_time == 15  # Solana is very fast
    
    @pytest.mark.asyncio
    async def test_sign_transaction_ethereum(self, usdc_service):
        """Test transaction signing for Ethereum"""
        transfer_request = TransferRequest(
            session_id="test_session_123",
            from_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            to_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            amount="100.00",
            chain_type="evm",
            chain_id="ethereum",
            currency="usdc",
            urgency="low",
            metadata={}
        )
        
        gas_estimate = GasEstimate(
            gas_price="20000000000",
            gas_limit=65000,
            total_cost="0.0013",
            estimated_time=60,
            max_priority_fee=None
        )
        
        with patch.object(usdc_service, '_create_ethereum_transaction', return_value="0x1234567890abcdef"):
            signed_tx = await usdc_service._sign_transaction(
                transfer_request, gas_estimate, "test_private_key"
            )
            
            assert signed_tx == "0x1234567890abcdef"
    
    @pytest.mark.asyncio
    async def test_sign_transaction_solana(self, usdc_service):
        """Test transaction signing for Solana"""
        transfer_request = TransferRequest(
            session_id="test_session_123",
            from_address="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
            to_address="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
            amount="100.00",
            chain_type="solana",
            chain_id="solana",
            currency="usdc",
            urgency="low",
            metadata={}
        )
        
        gas_estimate = GasEstimate(
            gas_price="5000",
            gas_limit=1,
            total_cost="0.000005",
            estimated_time=15,
            max_priority_fee=None
        )
        
        with patch.object(usdc_service, '_create_solana_transaction', return_value="5J1F7GHuZc1Lb4Jj6k9m2n3p4q5r6s7t8u9v0w1x2y3z4"):
            signed_tx = await usdc_service._sign_transaction(
                transfer_request, gas_estimate, "test_private_key"
            )
            
            assert signed_tx == "5J1F7GHuZc1Lb4Jj6k9m2n3p4q5r6s7t8u9v0w1x2y3z4"
    
    @pytest.mark.asyncio
    async def test_broadcast_transaction_ethereum(self, usdc_service):
        """Test transaction broadcasting for Ethereum"""
        mock_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        }
        
        mock_session = AsyncMock()
        mock_response_obj = AsyncMock()
        mock_response_obj.json.return_value = mock_response
        mock_session.post.return_value.__aenter__.return_value = mock_response_obj
        
        with patch.object(usdc_service, '_get_session', return_value=mock_session):
            tx_hash = await usdc_service._broadcast_ethereum_transaction(
                "0x1234567890abcdef",
                "ethereum"
            )
            
            assert tx_hash == "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    
    @pytest.mark.asyncio
    async def test_broadcast_transaction_solana(self, usdc_service):
        """Test transaction broadcasting for Solana"""
        mock_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": "5J1F7GHuZc1Lb4Jj6k9m2n3p4q5r6s7t8u9v0w1x2y3z4"
        }
        
        mock_session = AsyncMock()
        mock_response_obj = AsyncMock()
        mock_response_obj.json.return_value = mock_response
        mock_session.post.return_value.__aenter__.return_value = mock_response_obj
        
        with patch.object(usdc_service, '_get_session', return_value=mock_session):
            tx_hash = await usdc_service._broadcast_solana_transaction(
                "5J1F7GHuZc1Lb4Jj6k9m2n3p4q5r6s7t8u9v0w1x2y3z4"
            )
            
            assert tx_hash == "5J1F7GHuZc1Lb4Jj6k9m2n3p4q5r6s7t8u9v0w1x2y3z4"
    
    @pytest.mark.asyncio
    async def test_get_transaction_status_ethereum(self, usdc_service):
        """Test getting transaction status for Ethereum"""
        mock_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "blockNumber": "0x123456",
                "status": "0x1",
                "gasUsed": "0x186a0",
                "effectiveGasPrice": "0x4a817c800"
            }
        }
        
        mock_session = AsyncMock()
        mock_response_obj = AsyncMock()
        mock_response_obj.json.return_value = mock_response
        mock_session.post.return_value.__aenter__.return_value = mock_response_obj
        
        with patch.object(usdc_service, '_get_session', return_value=mock_session):
            status = await usdc_service._get_ethereum_transaction_status(
                "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                "ethereum"
            )
            
            assert status.status == "confirmed"
            assert status.block_number == 1193046
            assert status.gas_used == 100000
            assert status.effective_gas_price == "20000000000"
    
    @pytest.mark.asyncio
    async def test_get_transaction_status_solana(self, usdc_service):
        """Test getting transaction status for Solana"""
        mock_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "value": {
                    "slot": 123456789,
                    "meta": {
                        "err": None,
                        "fee": 5000,
                        "postBalances": [1000000000],
                        "preBalances": [1000005000]
                    }
                }
            }
        }
        
        mock_session = AsyncMock()
        mock_response_obj = AsyncMock()
        mock_response_obj.json.return_value = mock_response
        mock_session.post.return_value.__aenter__.return_value = mock_response_obj
        
        with patch.object(usdc_service, '_get_session', return_value=mock_session):
            status = await usdc_service._get_solana_transaction_status(
                "5J1F7GHuZc1Lb4Jj6k9m2n3p4q5r6s7t8u9v0w1x2y3z4"
            )
            
            assert status.status == "confirmed"
            assert status.slot == 123456789
            assert status.fee == 5000
            assert status.error is None

class TestTransferRequest:
    """Test TransferRequest class"""
    
    def test_transfer_request_creation(self):
        """Test creating a transfer request"""
        request = TransferRequest(
            session_id="test_session_123",
            from_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            to_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            amount="100.00",
            chain_type="evm",
            chain_id="ethereum",
            currency="usdc",
            urgency="low",
            metadata={"user_id": "test_user"}
        )
        
        assert request.session_id == "test_session_123"
        assert request.from_address == "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
        assert request.to_address == "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
        assert request.amount == "100.00"
        assert request.chain_type == "evm"
        assert request.chain_id == "ethereum"
        assert request.currency == "usdc"
        assert request.urgency == "low"
        assert request.metadata["user_id"] == "test_user"
    
    def test_transfer_request_validation(self):
        """Test transfer request validation"""
        # Valid request
        request = TransferRequest(
            session_id="test_session_123",
            from_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            to_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            amount="100.00",
            chain_type="evm",
            chain_id="ethereum",
            currency="usdc",
            urgency="low",
            metadata={}
        )
        
        assert request.is_valid() is True
        
        # Invalid amount
        request.amount = "invalid"
        assert request.is_valid() is False
        
        # Invalid address
        request.amount = "100.00"
        request.from_address = "invalid_address"
        assert request.is_valid() is False

class TestTransferResponse:
    """Test TransferResponse class"""
    
    def test_transfer_response_creation(self):
        """Test creating a transfer response"""
        response = TransferResponse(
            id="test_transfer_123",
            session_id="test_session_456",
            from_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            to_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            amount="100.00",
            chain_type="evm",
            chain_id="ethereum",
            currency="usdc",
            status="pending",
            transaction_hash="0x1234567890abcdef",
            gas_estimate=GasEstimate(
                gas_price="20000000000",
                gas_limit=65000,
                total_cost="0.0013",
                estimated_time=60
            ),
            created_at=datetime.utcnow()
        )
        
        assert response.id == "test_transfer_123"
        assert response.session_id == "test_session_456"
        assert response.status == "pending"
        assert response.transaction_hash == "0x1234567890abcdef"
        assert response.gas_estimate.gas_price == "20000000000"
    
    def test_transfer_response_to_dict(self):
        """Test converting transfer response to dictionary"""
        response = TransferResponse(
            id="test_transfer_123",
            session_id="test_session_456",
            from_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            to_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            amount="100.00",
            chain_type="evm",
            chain_id="ethereum",
            currency="usdc",
            status="pending",
            transaction_hash="0x1234567890abcdef",
            gas_estimate=GasEstimate(
                gas_price="20000000000",
                gas_limit=65000,
                total_cost="0.0013",
                estimated_time=60
            ),
            created_at=datetime.utcnow()
        )
        
        response_dict = response.to_dict()
        assert response_dict["id"] == "test_transfer_123"
        assert response_dict["status"] == "pending"
        assert response_dict["transaction_hash"] == "0x1234567890abcdef"

class TestGasEstimate:
    """Test GasEstimate class"""
    
    def test_gas_estimate_creation(self):
        """Test creating a gas estimate"""
        estimate = GasEstimate(
            gas_price="20000000000",
            gas_limit=65000,
            total_cost="0.0013",
            estimated_time=60,
            max_priority_fee="2000000000"
        )
        
        assert estimate.gas_price == "20000000000"
        assert estimate.gas_limit == 65000
        assert estimate.total_cost == "0.0013"
        assert estimate.estimated_time == 60
        assert estimate.max_priority_fee == "2000000000"
    
    def test_gas_estimate_calculation(self):
        """Test gas estimate calculation"""
        estimate = GasEstimate(
            gas_price="20000000000",  # 20 Gwei
            gas_limit=65000,
            total_cost="0.0013",
            estimated_time=60
        )
        
        # Calculate total cost in ETH
        gas_price_wei = int(estimate.gas_price)
        gas_limit = estimate.gas_limit
        total_cost_wei = gas_price_wei * gas_limit
        total_cost_eth = total_cost_wei / (10 ** 18)
        
        assert abs(total_cost_eth - 0.0013) < 0.0001

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

class TestNetworkConfig:
    """Test NetworkConfig class"""
    
    def test_network_config_creation(self):
        """Test creating a network config"""
        config = NetworkConfig(
            network_id="ethereum",
            name="Ethereum",
            type="evm",
            chain_id=1,
            currency="eth",
            status="active",
            rpc_url="https://eth-mainnet.alchemyapi.io/v2/...",
            contract_address="0xA0b86a33E6441b8c4C8C8C8C8C8C8C8C8C8C8C8C",
            min_amount="0.001",
            max_amount="10000"
        )
        
        assert config.network_id == "ethereum"
        assert config.name == "Ethereum"
        assert config.type == "evm"
        assert config.chain_id == 1
        assert config.currency == "eth"
        assert config.status == "active"
        assert config.rpc_url == "https://eth-mainnet.alchemyapi.io/v2/..."
        assert config.contract_address == "0xA0b86a33E6441b8c4C8C8C8C8C8C8C8C8C8C8C8C"
        assert config.min_amount == "0.001"
        assert config.max_amount == "10000"
    
    def test_network_config_validation(self):
        """Test network config validation"""
        config = NetworkConfig(
            network_id="ethereum",
            name="Ethereum",
            type="evm",
            chain_id=1,
            currency="eth",
            status="active",
            rpc_url="https://eth-mainnet.alchemyapi.io/v2/...",
            contract_address="0xA0b86a33E6441b8c4C8C8C8C8C8C8C8C8C8C8C8C",
            min_amount="0.001",
            max_amount="10000"
        )
        
        assert config.is_valid() is True
        
        # Invalid chain ID
        config.chain_id = -1
        assert config.is_valid() is False
        
        # Invalid contract address
        config.chain_id = 1
        config.contract_address = "invalid_address"
        assert config.is_valid() is False

class TestErrorHandling:
    """Test error handling"""
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self, usdc_service):
        """Test handling of network errors"""
        mock_session = AsyncMock()
        mock_session.post.side_effect = Exception("Network error")
        
        with patch.object(usdc_service, '_get_session', return_value=mock_session):
            with pytest.raises(Exception) as exc_info:
                await usdc_service._estimate_evm_gas(
                    chain_id="ethereum",
                    from_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                    to_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                    amount="100.00"
                )
            
            assert "Network error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_invalid_response_handling(self, usdc_service):
        """Test handling of invalid responses"""
        mock_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -32602,
                "message": "Invalid params"
            }
        }
        
        mock_session = AsyncMock()
        mock_response_obj = AsyncMock()
        mock_response_obj.json.return_value = mock_response
        mock_session.post.return_value.__aenter__.return_value = mock_response_obj
        
        with patch.object(usdc_service, '_get_session', return_value=mock_session):
            with pytest.raises(ValueError) as exc_info:
                await usdc_service._estimate_evm_gas(
                    chain_id="ethereum",
                    from_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                    to_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                    amount="100.00"
                )
            
            assert "Invalid params" in str(exc_info.value)

class TestIntegration:
    """Test integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_complete_transfer_flow_ethereum(self, usdc_service):
        """Test complete transfer flow for Ethereum"""
        transfer_request = TransferRequest(
            session_id="test_session_123",
            from_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            to_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            amount="100.00",
            chain_type="evm",
            chain_id="ethereum",
            currency="usdc",
            urgency="low",
            metadata={}
        )
        
        # Mock all the steps
        with patch.object(usdc_service, '_validate_transfer_request', return_value=True):
            with patch.object(usdc_service, '_estimate_gas', return_value=AsyncMock(
                gas_price="20000000000",
                gas_limit=65000,
                total_cost="0.0013",
                estimated_time=60
            )):
                with patch.object(usdc_service, '_sign_transaction', return_value="0x1234567890abcdef"):
                    with patch.object(usdc_service, '_broadcast_transaction', return_value="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"):
                        transfer = await usdc_service.create_usdc_transfer(transfer_request)
                        
                        assert transfer.status == "pending"
                        assert transfer.transaction_hash == "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    
    @pytest.mark.asyncio
    async def test_complete_transfer_flow_solana(self, usdc_service):
        """Test complete transfer flow for Solana"""
        transfer_request = TransferRequest(
            session_id="test_session_123",
            from_address="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
            to_address="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
            amount="100.00",
            chain_type="solana",
            chain_id="solana",
            currency="usdc",
            urgency="low",
            metadata={}
        )
        
        # Mock all the steps
        with patch.object(usdc_service, '_validate_transfer_request', return_value=True):
            with patch.object(usdc_service, '_estimate_gas', return_value=AsyncMock(
                gas_price="5000",
                gas_limit=1,
                total_cost="0.000005",
                estimated_time=15
            )):
                with patch.object(usdc_service, '_sign_transaction', return_value="5J1F7GHuZc1Lb4Jj6k9m2n3p4q5r6s7t8u9v0w1x2y3z4"):
                    with patch.object(usdc_service, '_broadcast_transaction', return_value="5J1F7GHuZc1Lb4Jj6k9m2n3p4q5r6s7t8u9v0w1x2y3z4"):
                        transfer = await usdc_service.create_usdc_transfer(transfer_request)
                        
                        assert transfer.status == "pending"
                        assert transfer.transaction_hash == "5J1F7GHuZc1Lb4Jj6k9m2n3p4q5r6s7t8u9v0w1x2y3z4" 