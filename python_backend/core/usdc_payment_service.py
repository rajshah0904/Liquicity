"""
USDC Payment Service
Production-level service for USDC transfers on EVM and Solana chains
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal
import aiohttp
from web3 import Web3, AsyncWeb3
from web3.exceptions import ContractLogicError, ValidationError
from solana.rpc.async_api import AsyncClient as SolanaClient
from solana.transaction import Transaction as SolanaTransaction
from solana.system_program import TransferParams, transfer
from solana.rpc.commitment import Commitment
import base64
import uuid

from config.settings import settings, ERROR_CODES, NETWORK_CONFIGS
from core.security import SecurityException, security_validator
from core.walletconnect_v2_service import WalletConnectV2Service, WalletConnectError

logger = logging.getLogger(__name__)

class USDCError(Exception):
    """Custom USDC payment exception"""
    
    def __init__(self, error_code: str, message: str, details: Optional[str] = None):
        self.error_code = error_code
        self.message = message
        self.details = details
        super().__init__(self.message)

class ChainType(str, Enum):
    EVM = "evm"
    SOLANA = "solana"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    SIGNED = "signed"
    BROADCASTED = "broadcasted"
    CONFIRMED = "confirmed"
    FAILED = "failed"

@dataclass
class GasEstimate:
    """Gas estimation result"""
    gas_price: str
    gas_limit: int
    total_cost: str
    estimated_time: int  # seconds
    max_priority_fee: Optional[str] = None

@dataclass
class USDCTransferRequest:
    """USDC transfer request"""
    id: str
    session_id: str
    from_address: str
    to_address: str
    amount: str
    chain_type: ChainType
    chain_id: str
    currency: str = "usdc"
    gas_estimate: Optional[GasEstimate] = None
    status: TransactionStatus = TransactionStatus.PENDING
    created_at: datetime = None
    signed_transaction: Optional[str] = None
    transaction_hash: Optional[str] = None
    confirmation_time: Optional[datetime] = None
    error_message: Optional[str] = None

class USDCContractAddresses:
    """Official USDC contract addresses"""
    
    EVM_ADDRESSES = {
        "ethereum": "0xA0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  # Mainnet USDC
        "polygon": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",   # Polygon USDC
        "base": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",      # Base USDC
        "arbitrum": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",  # Arbitrum USDC
        "optimism": "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85"   # Optimism USDC
    }
    
    SOLANA_ADDRESSES = {
        "solana": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # Solana USDC
    }

class USDCERC20ABI:
    """ERC20 ABI for USDC transfers"""
    
    TRANSFER_ABI = [
        {
            "constant": False,
            "inputs": [
                {"name": "_to", "type": "address"},
                {"name": "_value", "type": "uint256"}
            ],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "payable": False,
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        }
    ]

class USDCPaymentService:
    """
    Production USDC payment service
    Handles EVM and Solana USDC transfers with user-side signing
    """
    
    def __init__(self):
        self.walletconnect_service = WalletConnectV2Service()
        
        # Web3 clients for EVM chains
        self.web3_clients: Dict[str, AsyncWeb3] = {}
        
        # Solana client
        self.solana_client: Optional[SolanaClient] = None
        
        # Transaction storage
        self.transfers: Dict[str, USDCTransferRequest] = {}
        
        # Initialize clients
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Web3 and Solana clients"""
        
        # Initialize EVM clients
        for chain_id, config in NETWORK_CONFIGS.items():
            if chain_id in USDCContractAddresses.EVM_ADDRESSES:
                try:
                    self.web3_clients[chain_id] = AsyncWeb3(
                        AsyncWeb3.AsyncHTTPProvider(config["rpc_url"])
                    )
                    logger.info(f"Initialized Web3 client for {chain_id}")
                except Exception as e:
                    logger.error(f"Failed to initialize Web3 client for {chain_id}: {e}")
        
        # Initialize Solana client
        try:
            solana_config = NETWORK_CONFIGS.get("solana", {})
            self.solana_client = SolanaClient(solana_config.get("rpc_url"))
            logger.info("Initialized Solana client")
        except Exception as e:
            logger.error(f"Failed to initialize Solana client: {e}")
    
    async def create_usdc_transfer(
        self,
        session_id: str,
        to_address: str,
        amount: str,
        chain_id: str,
        currency: str = "usdc"
    ) -> USDCTransferRequest:
        """Create a USDC transfer request"""
        
        # Get session details
        session_data = await self.walletconnect_service.get_session_status(session_id)
        if not session_data:
            raise USDCError(
                error_code=ERROR_CODES["SESSION_EXPIRED"],
                message="Invalid session"
            )
        
        from_address = session_data["wallet_address"]
        chain_type = ChainType(session_data["chain_type"])
        
        # Validate addresses
        if not security_validator.validate_wallet_address(from_address, chain_id):
            raise USDCError(
                error_code=ERROR_CODES["INVALID_WALLET_ADDRESS"],
                message="Invalid sender address"
            )
        
        if not security_validator.validate_wallet_address(to_address, chain_id):
            raise USDCError(
                error_code=ERROR_CODES["INVALID_WALLET_ADDRESS"],
                message="Invalid recipient address"
            )
        
        # Validate amount
        try:
            amount_decimal = Decimal(amount)
            if amount_decimal <= 0:
                raise ValueError("Amount must be positive")
        except (ValueError, TypeError):
            raise USDCError(
                error_code=ERROR_CODES["INVALID_AMOUNT"],
                message="Invalid amount"
            )
        
        # Check balance
        await self._check_balance(from_address, amount, chain_id, chain_type)
        
        # Estimate gas
        gas_estimate = await self._estimate_gas(from_address, to_address, amount, chain_id, chain_type)
        
        # Create transfer request
        transfer_id = str(uuid.uuid4())
        transfer = USDCTransferRequest(
            id=transfer_id,
            session_id=session_id,
            from_address=from_address,
            to_address=to_address,
            amount=amount,
            chain_type=chain_type,
            chain_id=chain_id,
            currency=currency,
            gas_estimate=gas_estimate,
            created_at=datetime.utcnow()
        )
        
        # Store transfer
        self.transfers[transfer_id] = transfer
        
        logger.info(f"Created USDC transfer {transfer_id} for {amount} {currency}")
        return transfer
    
    async def _check_balance(
        self, 
        address: str, 
        amount: str, 
        chain_id: str, 
        chain_type: ChainType
    ):
        """Check if address has sufficient USDC balance"""
        
        if chain_type == ChainType.EVM:
            balance = await self._get_evm_usdc_balance(address, chain_id)
        else:
            balance = await self._get_solana_usdc_balance(address)
        
        amount_decimal = Decimal(amount)
        if balance < amount_decimal:
            raise USDCError(
                error_code=ERROR_CODES["INSUFFICIENT_BALANCE"],
                message=f"Insufficient USDC balance. Required: {amount}, Available: {balance}"
            )
    
    async def _get_evm_usdc_balance(self, address: str, chain_id: str) -> Decimal:
        """Get USDC balance on EVM chain"""
        
        if chain_id not in self.web3_clients:
            raise USDCError(
                error_code=ERROR_CODES["NETWORK_UNAVAILABLE"],
                message=f"Web3 client not available for {chain_id}"
            )
        
        if chain_id not in USDCContractAddresses.EVM_ADDRESSES:
            raise USDCError(
                error_code=ERROR_CODES["UNSUPPORTED_NETWORK"],
                message=f"USDC not supported on {chain_id}"
            )
        
        try:
            web3 = self.web3_clients[chain_id]
            contract_address = USDCContractAddresses.EVM_ADDRESSES[chain_id]
            
            # Create contract instance
            contract = web3.eth.contract(
                address=contract_address,
                abi=USDCERC20ABI.TRANSFER_ABI
            )
            
            # Get balance
            balance_wei = await contract.functions.balanceOf(address).call()
            decimals = await contract.functions.decimals().call()
            
            # Convert to decimal
            balance = Decimal(balance_wei) / (10 ** decimals)
            
            return balance
            
        except Exception as e:
            logger.error(f"Failed to get EVM USDC balance: {e}")
            raise USDCError(
                error_code=ERROR_CODES["BALANCE_CHECK_FAILED"],
                message=f"Failed to check USDC balance: {str(e)}"
            )
    
    async def _get_solana_usdc_balance(self, address: str) -> Decimal:
        """Get USDC balance on Solana"""
        
        if not self.solana_client:
            raise USDCError(
                error_code=ERROR_CODES["NETWORK_UNAVAILABLE"],
                message="Solana client not available"
            )
        
        try:
            # Get token accounts for the address
            response = await self.solana_client.get_token_accounts_by_owner(
                address,
                {"mint": USDCContractAddresses.SOLANA_ADDRESSES["solana"]}
            )
            
            if not response.value:
                return Decimal("0")
            
            # Get balance from the first token account
            token_account = response.value[0].pubkey
            balance_response = await self.solana_client.get_token_account_balance(token_account)
            
            balance_lamports = int(balance_response.value.amount)
            decimals = balance_response.value.decimals
            
            # Convert to decimal
            balance = Decimal(balance_lamports) / (10 ** decimals)
            
            return balance
            
        except Exception as e:
            logger.error(f"Failed to get Solana USDC balance: {e}")
            raise USDCError(
                error_code=ERROR_CODES["BALANCE_CHECK_FAILED"],
                message=f"Failed to check Solana USDC balance: {str(e)}"
            )
    
    async def _estimate_gas(
        self,
        from_address: str,
        to_address: str,
        amount: str,
        chain_id: str,
        chain_type: ChainType
    ) -> GasEstimate:
        """Estimate gas for USDC transfer"""
        
        if chain_type == ChainType.EVM:
            return await self._estimate_evm_gas(from_address, to_address, amount, chain_id)
        else:
            return await self._estimate_solana_gas(amount)
    
    async def _estimate_evm_gas(
        self,
        from_address: str,
        to_address: str,
        amount: str,
        chain_id: str
    ) -> GasEstimate:
        """Estimate gas for EVM USDC transfer"""
        
        if chain_id not in self.web3_clients:
            raise USDCError(
                error_code=ERROR_CODES["NETWORK_UNAVAILABLE"],
                message=f"Web3 client not available for {chain_id}"
            )
        
        try:
            web3 = self.web3_clients[chain_id]
            contract_address = USDCContractAddresses.EVM_ADDRESSES[chain_id]
            
            # Create contract instance
            contract = web3.eth.contract(
                address=contract_address,
                abi=USDCERC20ABI.TRANSFER_ABI
            )
            
            # Get decimals
            decimals = await contract.functions.decimals().call()
            
            # Convert amount to wei
            amount_wei = int(Decimal(amount) * (10 ** decimals))
            
            # Build transaction
            transaction = contract.functions.transfer(to_address, amount_wei).build_transaction({
                'from': from_address,
                'nonce': await web3.eth.get_transaction_count(from_address),
                'gas': 100000,  # Initial estimate
                'gasPrice': await web3.eth.gas_price
            })
            
            # Estimate gas
            gas_estimate = await web3.eth.estimate_gas(transaction)
            
            # Get current gas price
            gas_price = await web3.eth.gas_price
            
            # Calculate total cost
            total_cost_wei = gas_estimate * gas_price
            total_cost_eth = web3.from_wei(total_cost_wei, 'ether')
            
            return GasEstimate(
                gas_price=str(gas_price),
                gas_limit=gas_estimate,
                total_cost=str(total_cost_eth),
                estimated_time=60,  # 1 minute for EVM
                max_priority_fee=None
            )
            
        except Exception as e:
            logger.error(f"Failed to estimate EVM gas: {e}")
            raise USDCError(
                error_code=ERROR_CODES["GAS_ESTIMATION_FAILED"],
                message=f"Failed to estimate gas: {str(e)}"
            )
    
    async def _estimate_solana_gas(self, amount: str) -> GasEstimate:
        """Estimate gas for Solana USDC transfer"""
        
        if not self.solana_client:
            raise USDCError(
                error_code=ERROR_CODES["NETWORK_UNAVAILABLE"],
                message="Solana client not available"
            )
        
        try:
            # Solana has very low fees, typically around 5000 lamports
            gas_price = 5000  # lamports
            gas_limit = 1
            
            # Convert to SOL
            total_cost_lamports = gas_price * gas_limit
            total_cost_sol = total_cost_lamports / (10 ** 9)  # 9 decimals for SOL
            
            return GasEstimate(
                gas_price=str(gas_price),
                gas_limit=gas_limit,
                total_cost=str(total_cost_sol),
                estimated_time=1,  # 1 second for Solana
                max_priority_fee=None
            )
            
        except Exception as e:
            logger.error(f"Failed to estimate Solana gas: {e}")
            raise USDCError(
                error_code=ERROR_CODES["GAS_ESTIMATION_FAILED"],
                message=f"Failed to estimate Solana gas: {str(e)}"
            )
    
    async def build_transaction(self, transfer_id: str) -> Dict[str, Any]:
        """Build transaction for signing"""
        
        if transfer_id not in self.transfers:
            raise USDCError(
                error_code=ERROR_CODES["TRANSFER_NOT_FOUND"],
                message="Transfer not found"
            )
        
        transfer = self.transfers[transfer_id]
        
        if transfer.chain_type == ChainType.EVM:
            return await self._build_evm_transaction(transfer)
        else:
            return await self._build_solana_transaction(transfer)
    
    async def _build_evm_transaction(self, transfer: USDCTransferRequest) -> Dict[str, Any]:
        """Build EVM transaction"""
        
        if transfer.chain_id not in self.web3_clients:
            raise USDCError(
                error_code=ERROR_CODES["NETWORK_UNAVAILABLE"],
                message=f"Web3 client not available for {transfer.chain_id}"
            )
        
        try:
            web3 = self.web3_clients[transfer.chain_id]
            contract_address = USDCContractAddresses.EVM_ADDRESSES[transfer.chain_id]
            
            # Create contract instance
            contract = web3.eth.contract(
                address=contract_address,
                abi=USDCERC20ABI.TRANSFER_ABI
            )
            
            # Get decimals
            decimals = await contract.functions.decimals().call()
            
            # Convert amount to wei
            amount_wei = int(Decimal(transfer.amount) * (10 ** decimals))
            
            # Get nonce
            nonce = await web3.eth.get_transaction_count(transfer.from_address)
            
            # Build transaction
            transaction = contract.functions.transfer(transfer.to_address, amount_wei).build_transaction({
                'from': transfer.from_address,
                'nonce': nonce,
                'gas': transfer.gas_estimate.gas_limit if transfer.gas_estimate else 100000,
                'gasPrice': int(transfer.gas_estimate.gas_price) if transfer.gas_estimate else await web3.eth.gas_price
            })
            
            return {
                "chain_type": "evm",
                "chain_id": transfer.chain_id,
                "transaction": transaction,
                "to": contract_address,
                "value": "0",  # USDC transfers have 0 ETH value
                "data": transaction['data']
            }
            
        except Exception as e:
            logger.error(f"Failed to build EVM transaction: {e}")
            raise USDCError(
                error_code=ERROR_CODES["TRANSACTION_BUILD_FAILED"],
                message=f"Failed to build transaction: {str(e)}"
            )
    
    async def _build_solana_transaction(self, transfer: USDCTransferRequest) -> Dict[str, Any]:
        """Build Solana transaction"""
        
        if not self.solana_client:
            raise USDCError(
                error_code=ERROR_CODES["NETWORK_UNAVAILABLE"],
                message="Solana client not available"
            )
        
        try:
            # Create Solana transaction
            transaction = SolanaTransaction()
            
            # Add USDC transfer instruction
            transfer_instruction = transfer(
                TransferParams(
                    from_pubkey=transfer.from_address,
                    to_pubkey=transfer.to_address,
                    lamports=int(Decimal(transfer.amount) * (10 ** 6))  # USDC has 6 decimals
                )
            )
            
            transaction.add(transfer_instruction)
            
            return {
                "chain_type": "solana",
                "chain_id": transfer.chain_id,
                "transaction": transaction,
                "instructions": [transfer_instruction]
            }
            
        except Exception as e:
            logger.error(f"Failed to build Solana transaction: {e}")
            raise USDCError(
                error_code=ERROR_CODES["TRANSACTION_BUILD_FAILED"],
                message=f"Failed to build Solana transaction: {str(e)}"
            )
    
    async def process_signed_transaction(
        self,
        transfer_id: str,
        signed_transaction: str
    ) -> Dict[str, Any]:
        """Process signed transaction and broadcast to network"""
        
        if transfer_id not in self.transfers:
            raise USDCError(
                error_code=ERROR_CODES["TRANSFER_NOT_FOUND"],
                message="Transfer not found"
            )
        
        transfer = self.transfers[transfer_id]
        transfer.signed_transaction = signed_transaction
        
        try:
            if transfer.chain_type == ChainType.EVM:
                result = await self._broadcast_evm_transaction(transfer)
            else:
                result = await self._broadcast_solana_transaction(transfer)
            
            transfer.status = TransactionStatus.BROADCASTED
            transfer.transaction_hash = result.get("transaction_hash")
            
            return result
            
        except Exception as e:
            transfer.status = TransactionStatus.FAILED
            transfer.error_message = str(e)
            raise
    
    async def _broadcast_evm_transaction(self, transfer: USDCTransferRequest) -> Dict[str, Any]:
        """Broadcast EVM transaction"""
        
        if transfer.chain_id not in self.web3_clients:
            raise USDCError(
                error_code=ERROR_CODES["NETWORK_UNAVAILABLE"],
                message=f"Web3 client not available for {transfer.chain_id}"
            )
        
        try:
            web3 = self.web3_clients[transfer.chain_id]
            
            # Send raw transaction
            tx_hash = await web3.eth.send_raw_transaction(transfer.signed_transaction)
            
            # Wait for confirmation
            receipt = await web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status == 1:
                transfer.status = TransactionStatus.CONFIRMED
                transfer.confirmation_time = datetime.utcnow()
                return {
                    "transaction_hash": tx_hash.hex(),
                    "status": "confirmed",
                    "block_number": receipt.blockNumber,
                    "gas_used": receipt.gasUsed
                }
            else:
                transfer.status = TransactionStatus.FAILED
                raise USDCError(
                    error_code=ERROR_CODES["TRANSACTION_FAILED"],
                    message="Transaction failed on chain"
                )
                
        except Exception as e:
            logger.error(f"Failed to broadcast EVM transaction: {e}")
            raise USDCError(
                error_code=ERROR_CODES["BROADCAST_FAILED"],
                message=f"Failed to broadcast transaction: {str(e)}"
            )
    
    async def _broadcast_solana_transaction(self, transfer: USDCTransferRequest) -> Dict[str, Any]:
        """Broadcast Solana transaction"""
        
        if not self.solana_client:
            raise USDCError(
                error_code=ERROR_CODES["NETWORK_UNAVAILABLE"],
                message="Solana client not available"
            )
        
        try:
            # Send transaction
            result = await self.solana_client.send_raw_transaction(
                transfer.signed_transaction,
                opts={"skip_confirmation": False, "preflight_commitment": Commitment("confirmed")}
            )
            
            if result.value:
                transfer.status = TransactionStatus.CONFIRMED
                transfer.confirmation_time = datetime.utcnow()
                return {
                    "transaction_hash": result.value,
                    "status": "confirmed"
                }
            else:
                transfer.status = TransactionStatus.FAILED
                raise USDCError(
                    error_code=ERROR_CODES["TRANSACTION_FAILED"],
                    message="Solana transaction failed"
                )
                
        except Exception as e:
            logger.error(f"Failed to broadcast Solana transaction: {e}")
            raise USDCError(
                error_code=ERROR_CODES["BROADCAST_FAILED"],
                message=f"Failed to broadcast Solana transaction: {str(e)}"
            )
    
    async def get_transfer_status(self, transfer_id: str) -> Optional[Dict[str, Any]]:
        """Get transfer status"""
        
        if transfer_id not in self.transfers:
            return None
        
        transfer = self.transfers[transfer_id]
        
        return {
            "transfer_id": transfer.id,
            "session_id": transfer.session_id,
            "from_address": transfer.from_address,
            "to_address": transfer.to_address,
            "amount": transfer.amount,
            "currency": transfer.currency,
            "chain_type": transfer.chain_type.value,
            "chain_id": transfer.chain_id,
            "status": transfer.status.value,
            "created_at": transfer.created_at.isoformat() if transfer.created_at else None,
            "signed_transaction": transfer.signed_transaction,
            "transaction_hash": transfer.transaction_hash,
            "confirmation_time": transfer.confirmation_time.isoformat() if transfer.confirmation_time else None,
            "error_message": transfer.error_message,
            "gas_estimate": {
                "gas_price": transfer.gas_estimate.gas_price,
                "gas_limit": transfer.gas_estimate.gas_limit,
                "total_cost": transfer.gas_estimate.total_cost,
                "estimated_time": transfer.gas_estimate.estimated_time
            } if transfer.gas_estimate else None
        }

# Global service instance
usdc_payment_service = USDCPaymentService() 