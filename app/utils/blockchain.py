import os
import json
from typing import Dict, List, Optional, Any, Union
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_account.signers.local import LocalAccount
import eth_utils
from fastapi import HTTPException
import requests
import time
from app.config import AppConfig

config = AppConfig()

# Load provider URLs from environment variables
ETH_MAINNET_RPC = os.getenv("ETH_MAINNET_RPC", "https://mainnet.infura.io/v3/your-key")
ETH_TESTNET_RPC = os.getenv("ETH_GOERLI_RPC", "https://goerli.infura.io/v3/your-key")
POLYGON_MAINNET_RPC = os.getenv("POLYGON_MAINNET_RPC", "https://polygon-rpc.com")
POLYGON_TESTNET_RPC = os.getenv("POLYGON_MUMBAI_RPC", "https://rpc-mumbai.maticvigil.com")

# ABI directories
ABI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../abis")

class BlockchainService:
    """Service for interacting with EVM-compatible blockchains"""
    
    def __init__(self, network: str = "ethereum", testnet: bool = False):
        """
        Initialize blockchain service
        
        Args:
            network: Blockchain network ("ethereum", "polygon", "avalanche")
            testnet: Whether to use testnet
        """
        self.network = network
        self.testnet = testnet
        self.provider_url = self._get_provider_url()
        self.web3 = Web3(Web3.HTTPProvider(self.provider_url))
        
        # Add PoA middleware for testnets
        if testnet:
            self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Check connection
        if not self.web3.isConnected():
            print(f"Warning: Could not connect to {network}{' testnet' if testnet else ''}")
    
    def _get_provider_url(self) -> str:
        """Get provider URL based on network and testnet flag"""
        if self.network == "ethereum":
            return ETH_TESTNET_RPC if self.testnet else ETH_MAINNET_RPC
        elif self.network == "polygon":
            return POLYGON_TESTNET_RPC if self.testnet else POLYGON_MAINNET_RPC
        else:
            # Default to Ethereum
            return ETH_TESTNET_RPC if self.testnet else ETH_MAINNET_RPC
    
    def get_erc20_contract(self, token_address: str):
        """Get ERC20 token contract instance"""
        with open(os.path.join(ABI_DIR, "erc20.json"), "r") as f:
            erc20_abi = json.load(f)
        
        # Validate and checksum address
        if not Web3.isAddress(token_address):
            raise ValueError(f"Invalid token address: {token_address}")
        
        checksum_address = Web3.toChecksumAddress(token_address)
        return self.web3.eth.contract(address=checksum_address, abi=erc20_abi)
    
    def get_payment_processor_contract(self, contract_address: str):
        """Get Liquicity payment processor contract instance"""
        try:
            with open(os.path.join(ABI_DIR, "LiquicityPaymentProcessor.json"), "r") as f:
                processor_abi = json.load(f)
            
            # Validate and checksum address
            if not Web3.isAddress(contract_address):
                raise ValueError(f"Invalid contract address: {contract_address}")
            
            checksum_address = Web3.toChecksumAddress(contract_address)
            return self.web3.eth.contract(address=checksum_address, abi=processor_abi)
        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="Payment processor ABI not found")
    
    def get_swap_contract(self, contract_address: str):
        """Get Liquicity swap contract instance"""
        try:
            with open(os.path.join(ABI_DIR, "LiquicitySwap.json"), "r") as f:
                swap_abi = json.load(f)
            
            # Validate and checksum address
            if not Web3.isAddress(contract_address):
                raise ValueError(f"Invalid contract address: {contract_address}")
            
            checksum_address = Web3.toChecksumAddress(contract_address)
            return self.web3.eth.contract(address=checksum_address, abi=swap_abi)
        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="Swap contract ABI not found")
    
    def create_account(self) -> Dict[str, str]:
        """Create a new Ethereum account"""
        account: LocalAccount = Account.create()
        return {
            "address": account.address,
            "private_key": account.key.hex()  # WARNING: Handle private keys securely!
        }
    
    def get_eth_balance(self, address: str) -> float:
        """Get ETH balance for an address"""
        if not Web3.isAddress(address):
            raise ValueError(f"Invalid address: {address}")
        
        checksum_address = Web3.toChecksumAddress(address)
        balance_wei = self.web3.eth.get_balance(checksum_address)
        return float(self.web3.fromWei(balance_wei, "ether"))
    
    def get_token_balance(self, token_address: str, wallet_address: str) -> float:
        """Get ERC20 token balance for an address"""
        # Get token contract
        token_contract = self.get_erc20_contract(token_address)
        checksum_address = Web3.toChecksumAddress(wallet_address)
        
        # Get token details
        try:
            symbol = token_contract.functions.symbol().call()
            decimals = token_contract.functions.decimals().call()
            balance = token_contract.functions.balanceOf(checksum_address).call()
            
            # Convert to float with proper decimals
            return float(balance) / (10 ** decimals)
        except Exception as e:
            print(f"Error getting token balance: {str(e)}")
            return 0.0
    
    def send_token(
        self, 
        token_address: str, 
        from_address: str,
        to_address: str,
        amount: float,
        private_key: str,
        gas_price_gwei: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send ERC20 tokens
        
        Args:
            token_address: Token contract address
            from_address: Sender address
            to_address: Recipient address
            amount: Amount of tokens to send
            private_key: Sender's private key
            gas_price_gwei: Gas price in gwei (optional)
        
        Returns:
            Transaction details
        """
        # Check addresses
        if not Web3.isAddress(token_address) or not Web3.isAddress(from_address) or not Web3.isAddress(to_address):
            raise ValueError("Invalid address provided")
        
        # Get token contract
        token_contract = self.get_erc20_contract(token_address)
        
        # Convert addresses to checksum format
        checksum_token = Web3.toChecksumAddress(token_address)
        checksum_from = Web3.toChecksumAddress(from_address)
        checksum_to = Web3.toChecksumAddress(to_address)
        
        # Get token details
        try:
            symbol = token_contract.functions.symbol().call()
            decimals = token_contract.functions.decimals().call()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting token details: {str(e)}")
        
        # Convert amount to token units
        amount_in_units = int(amount * (10 ** decimals))
        
        # Check if sender has enough balance
        balance = token_contract.functions.balanceOf(checksum_from).call()
        if balance < amount_in_units:
            raise HTTPException(status_code=400, detail=f"Insufficient {symbol} balance")
        
        # Build transaction
        try:
            # Prepare function call
            transfer_function = token_contract.functions.transfer(
                checksum_to,
                amount_in_units
            )
            
            # Get gas price
            if gas_price_gwei:
                gas_price = self.web3.toWei(gas_price_gwei, "gwei")
            else:
                gas_price = self.web3.eth.gas_price
            
            # Build transaction
            tx = transfer_function.buildTransaction({
                'from': checksum_from,
                'nonce': self.web3.eth.get_transaction_count(checksum_from),
                'gas': 100000,  # Standard ERC20 transfer uses ~65000 gas
                'gasPrice': gas_price,
                'chainId': self.web3.eth.chain_id
            })
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            # Return transaction details
            return {
                'transaction_hash': tx_hash.hex(),
                'from': checksum_from,
                'to': checksum_to,
                'token_address': checksum_token,
                'amount': amount,
                'symbol': symbol,
                'status': 'success' if receipt.status == 1 else 'failed',
                'block_number': receipt.blockNumber,
                'gas_used': receipt.gasUsed
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")
    
    def process_payment(
        self,
        processor_address: str,
        token_address: str,
        sender_address: str,
        recipient_address: str,
        amount: float,
        reference: str,
        private_key: str,
        gas_price_gwei: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process a payment through the Liquicity payment processor
        
        Args:
            processor_address: Payment processor contract address
            token_address: Token contract address
            sender_address: Sender address
            recipient_address: Recipient address
            amount: Amount of tokens to send
            reference: Payment reference string
            private_key: Sender's private key
            gas_price_gwei: Gas price in gwei (optional)
        
        Returns:
            Transaction details
        """
        # Check addresses
        if not Web3.isAddress(processor_address) or not Web3.isAddress(token_address) or \
           not Web3.isAddress(sender_address) or not Web3.isAddress(recipient_address):
            raise ValueError("Invalid address provided")
        
        # Get contract instances
        processor_contract = self.get_payment_processor_contract(processor_address)
        token_contract = self.get_erc20_contract(token_address)
        
        # Convert addresses to checksum format
        checksum_processor = Web3.toChecksumAddress(processor_address)
        checksum_token = Web3.toChecksumAddress(token_address)
        checksum_sender = Web3.toChecksumAddress(sender_address)
        checksum_recipient = Web3.toChecksumAddress(recipient_address)
        
        # Get token details
        try:
            symbol = token_contract.functions.symbol().call()
            decimals = token_contract.functions.decimals().call()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting token details: {str(e)}")
        
        # Convert amount to token units
        amount_in_units = int(amount * (10 ** decimals))
        
        # Check if token is supported
        try:
            is_supported = processor_contract.functions.supportedTokens(checksum_token).call()
            if not is_supported:
                raise HTTPException(status_code=400, detail=f"Token {symbol} not supported by payment processor")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error checking token support: {str(e)}")
        
        # Check if sender has enough balance and approved the contract
        try:
            balance = token_contract.functions.balanceOf(checksum_sender).call()
            if balance < amount_in_units:
                raise HTTPException(status_code=400, detail=f"Insufficient {symbol} balance")
            
            allowance = token_contract.functions.allowance(checksum_sender, checksum_processor).call()
            if allowance < amount_in_units:
                # Need to approve the contract first
                approve_tx = token_contract.functions.approve(
                    checksum_processor,
                    amount_in_units
                ).buildTransaction({
                    'from': checksum_sender,
                    'nonce': self.web3.eth.get_transaction_count(checksum_sender),
                    'gas': 100000,
                    'gasPrice': self.web3.eth.gas_price if gas_price_gwei is None else self.web3.toWei(gas_price_gwei, "gwei"),
                    'chainId': self.web3.eth.chain_id
                })
                
                signed_approve_tx = self.web3.eth.account.sign_transaction(approve_tx, private_key)
                approve_tx_hash = self.web3.eth.send_raw_transaction(signed_approve_tx.rawTransaction)
                approve_receipt = self.web3.eth.wait_for_transaction_receipt(approve_tx_hash, timeout=120)
                
                if approve_receipt.status != 1:
                    raise HTTPException(status_code=500, detail="Token approval failed")
                
                # Update nonce for the next transaction
                nonce = self.web3.eth.get_transaction_count(checksum_sender)
            else:
                nonce = self.web3.eth.get_transaction_count(checksum_sender)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error checking balance or allowance: {str(e)}")
        
        # Process payment
        try:
            # Prepare function call
            payment_function = processor_contract.functions.processPayment(
                checksum_token,
                checksum_recipient,
                amount_in_units,
                reference
            )
            
            # Get gas price
            if gas_price_gwei:
                gas_price = self.web3.toWei(gas_price_gwei, "gwei")
            else:
                gas_price = self.web3.eth.gas_price
            
            # Build transaction
            tx = payment_function.buildTransaction({
                'from': checksum_sender,
                'nonce': nonce,
                'gas': 200000,  # Payment processing uses more gas than a simple transfer
                'gasPrice': gas_price,
                'chainId': self.web3.eth.chain_id
            })
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            # Return transaction details
            return {
                'transaction_hash': tx_hash.hex(),
                'from': checksum_sender,
                'to': checksum_recipient,
                'processor': checksum_processor,
                'token_address': checksum_token,
                'amount': amount,
                'symbol': symbol,
                'reference': reference,
                'status': 'success' if receipt.status == 1 else 'failed',
                'block_number': receipt.blockNumber,
                'gas_used': receipt.gasUsed
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")

# Global blockchain service instances
_blockchain_services = {}

def get_blockchain_service(network: str = "ethereum", testnet: bool = False) -> BlockchainService:
    """Get or create a blockchain service instance"""
    key = f"{network}-{'testnet' if testnet else 'mainnet'}"
    if key not in _blockchain_services:
        _blockchain_services[key] = BlockchainService(network, testnet)
    return _blockchain_services[key] 