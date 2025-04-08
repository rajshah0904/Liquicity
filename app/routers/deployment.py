from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.utils.blockchain import get_blockchain_service
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, validator
import os
import json
import time
import re

router = APIRouter()

# Path to contract artifacts directory
CONTRACTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "contracts")

class DeployTokenRequest(BaseModel):
    """Request model for deploying the TerraFlow token contract"""
    deployer_address: str
    private_key: str  # WARNING: Handle with extreme care
    network: str = "ethereum"  # ethereum, polygon, avalanche
    testnet: bool = True  # Default to testnet for safety
    gas_price_gwei: Optional[int] = None
    
    @validator('deployer_address')
    def validate_ethereum_address(cls, v):
        if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
            raise ValueError(f"Invalid Ethereum address format: {v}")
        return v

class DeployProcessorRequest(BaseModel):
    """Request model for deploying the TerraFlow payment processor contract"""
    deployer_address: str
    fee_recipient_address: str  # Address that will receive fees
    private_key: str  # WARNING: Handle with extreme care
    network: str = "ethereum"  # ethereum, polygon, avalanche
    testnet: bool = True  # Default to testnet for safety
    gas_price_gwei: Optional[int] = None
    
    @validator('deployer_address', 'fee_recipient_address')
    def validate_ethereum_address(cls, v):
        if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
            raise ValueError(f"Invalid Ethereum address format: {v}")
        return v

class ConfigureProcessorRequest(BaseModel):
    """Request model for configuring the payment processor contract"""
    processor_address: str
    token_address: str
    is_supported: bool = True
    deployer_address: str
    private_key: str
    network: str = "ethereum"
    testnet: bool = True
    gas_price_gwei: Optional[int] = None
    
    @validator('processor_address', 'token_address', 'deployer_address')
    def validate_ethereum_address(cls, v):
        if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
            raise ValueError(f"Invalid Ethereum address format: {v}")
        return v

class DeploymentStatus(BaseModel):
    """Model for tracking deployment status"""
    deployment_id: str
    contract_name: str
    status: str  # pending, in_progress, completed, failed
    address: Optional[str] = None
    transaction_hash: Optional[str] = None
    error_message: Optional[str] = None
    details: Dict[str, Any] = {}

# In-memory store for deployment statuses
# In production, use a proper database
deployment_statuses: Dict[str, DeploymentStatus] = {}

def generate_deployment_id() -> str:
    """Generate a unique deployment ID"""
    return f"deploy-{int(time.time())}-{os.urandom(4).hex()}"

async def deploy_token_contract(
    deployment_id: str,
    deployer_address: str,
    private_key: str,
    network: str,
    testnet: bool,
    gas_price_gwei: Optional[int]
):
    """Background task to deploy the TerraFlow token contract"""
    try:
        # Update status to in progress
        deployment_statuses[deployment_id].status = "in_progress"
        
        # Get blockchain service
        blockchain_service = get_blockchain_service(network=network, testnet=testnet)
        
        # Get contract ABI and bytecode
        try:
            token_artifact_path = os.path.join(CONTRACTS_DIR, "artifacts", "TerraFlowToken.json")
            with open(token_artifact_path, "r") as f:
                artifact = json.load(f)
                abi = artifact["abi"]
                bytecode = artifact["bytecode"]
        except FileNotFoundError:
            raise Exception("Contract artifact not found. Run 'npx hardhat compile' in the contracts directory.")
        
        # Deploy contract
        web3 = blockchain_service.web3
        checksum_address = web3.toChecksumAddress(deployer_address)
        
        # Create contract instance
        token_contract = web3.eth.contract(abi=abi, bytecode=bytecode)
        
        # Build constructor transaction
        nonce = web3.eth.get_transaction_count(checksum_address)
        gas_price = web3.eth.gas_price if gas_price_gwei is None else web3.toWei(gas_price_gwei, "gwei")
        
        # Estimate gas for deployment
        gas_estimate = token_contract.constructor().estimateGas({'from': checksum_address})
        
        # Prepare transaction
        transaction = token_contract.constructor().buildTransaction({
            'from': checksum_address,
            'nonce': nonce,
            'gas': int(gas_estimate * 1.2),  # Add 20% buffer
            'gasPrice': gas_price,
            'chainId': web3.eth.chain_id
        })
        
        # Sign and send transaction
        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
        txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Update status with transaction hash
        deployment_statuses[deployment_id].transaction_hash = txn_hash.hex()
        
        # Wait for transaction receipt
        receipt = web3.eth.wait_for_transaction_receipt(txn_hash, timeout=300)
        
        if receipt.status == 1:
            # Contract successfully deployed
            contract_address = receipt.contractAddress
            
            # Update deployment status
            deployment_statuses[deployment_id].status = "completed"
            deployment_statuses[deployment_id].address = contract_address
            deployment_statuses[deployment_id].details = {
                "transaction_hash": txn_hash.hex(),
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "contract_name": "TerraFlowToken",
                "deployer": deployer_address,
                "network": network,
                "testnet": testnet
            }
        else:
            # Deployment failed
            deployment_statuses[deployment_id].status = "failed"
            deployment_statuses[deployment_id].error_message = "Transaction reverted"
            
    except Exception as e:
        # Update status to failed
        deployment_statuses[deployment_id].status = "failed"
        deployment_statuses[deployment_id].error_message = str(e)

async def deploy_processor_contract(
    deployment_id: str,
    deployer_address: str,
    fee_recipient_address: str,
    private_key: str,
    network: str,
    testnet: bool,
    gas_price_gwei: Optional[int]
):
    """Background task to deploy the TerraFlow payment processor contract"""
    try:
        # Update status to in progress
        deployment_statuses[deployment_id].status = "in_progress"
        
        # Get blockchain service
        blockchain_service = get_blockchain_service(network=network, testnet=testnet)
        
        # Get contract ABI and bytecode
        try:
            processor_artifact_path = os.path.join(CONTRACTS_DIR, "artifacts", "TerraFlowPaymentProcessor.json")
            with open(processor_artifact_path, "r") as f:
                artifact = json.load(f)
                abi = artifact["abi"]
                bytecode = artifact["bytecode"]
        except FileNotFoundError:
            raise Exception("Contract artifact not found. Run 'npx hardhat compile' in the contracts directory.")
        
        # Deploy contract
        web3 = blockchain_service.web3
        checksum_address = web3.toChecksumAddress(deployer_address)
        checksum_fee_recipient = web3.toChecksumAddress(fee_recipient_address)
        
        # Create contract instance
        processor_contract = web3.eth.contract(abi=abi, bytecode=bytecode)
        
        # Build constructor transaction
        nonce = web3.eth.get_transaction_count(checksum_address)
        gas_price = web3.eth.gas_price if gas_price_gwei is None else web3.toWei(gas_price_gwei, "gwei")
        
        # Estimate gas for deployment
        gas_estimate = processor_contract.constructor(checksum_fee_recipient).estimateGas({'from': checksum_address})
        
        # Prepare transaction
        transaction = processor_contract.constructor(checksum_fee_recipient).buildTransaction({
            'from': checksum_address,
            'nonce': nonce,
            'gas': int(gas_estimate * 1.2),  # Add 20% buffer
            'gasPrice': gas_price,
            'chainId': web3.eth.chain_id
        })
        
        # Sign and send transaction
        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
        txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Update status with transaction hash
        deployment_statuses[deployment_id].transaction_hash = txn_hash.hex()
        
        # Wait for transaction receipt
        receipt = web3.eth.wait_for_transaction_receipt(txn_hash, timeout=300)
        
        if receipt.status == 1:
            # Contract successfully deployed
            contract_address = receipt.contractAddress
            
            # Update deployment status
            deployment_statuses[deployment_id].status = "completed"
            deployment_statuses[deployment_id].address = contract_address
            deployment_statuses[deployment_id].details = {
                "transaction_hash": txn_hash.hex(),
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "contract_name": "TerraFlowPaymentProcessor",
                "deployer": deployer_address,
                "fee_recipient": fee_recipient_address,
                "network": network,
                "testnet": testnet
            }
        else:
            # Deployment failed
            deployment_statuses[deployment_id].status = "failed"
            deployment_statuses[deployment_id].error_message = "Transaction reverted"
            
    except Exception as e:
        # Update status to failed
        deployment_statuses[deployment_id].status = "failed"
        deployment_statuses[deployment_id].error_message = str(e)

@router.post("/token")
async def deploy_token(
    request: DeployTokenRequest,
    background_tasks: BackgroundTasks,
    username: str = Depends(get_current_user)
):
    """
    Deploy the TerraFlow token contract
    
    Deploys the ERC20 token contract for the TerraFlow platform.
    This is a long-running operation that runs in the background.
    """
    # Generate deployment ID
    deployment_id = generate_deployment_id()
    
    # Create initial status
    deployment_statuses[deployment_id] = DeploymentStatus(
        deployment_id=deployment_id,
        contract_name="TerraFlowToken",
        status="pending"
    )
    
    # Start deployment in background
    background_tasks.add_task(
        deploy_token_contract,
        deployment_id=deployment_id,
        deployer_address=request.deployer_address,
        private_key=request.private_key,
        network=request.network,
        testnet=request.testnet,
        gas_price_gwei=request.gas_price_gwei
    )
    
    return {
        "message": "Token deployment started",
        "deployment_id": deployment_id,
        "status": "pending"
    }

@router.post("/processor")
async def deploy_payment_processor(
    request: DeployProcessorRequest,
    background_tasks: BackgroundTasks,
    username: str = Depends(get_current_user)
):
    """
    Deploy the TerraFlow payment processor contract
    
    Deploys the payment processor contract for handling payments.
    This is a long-running operation that runs in the background.
    """
    # Generate deployment ID
    deployment_id = generate_deployment_id()
    
    # Create initial status
    deployment_statuses[deployment_id] = DeploymentStatus(
        deployment_id=deployment_id,
        contract_name="TerraFlowPaymentProcessor",
        status="pending"
    )
    
    # Start deployment in background
    background_tasks.add_task(
        deploy_processor_contract,
        deployment_id=deployment_id,
        deployer_address=request.deployer_address,
        fee_recipient_address=request.fee_recipient_address,
        private_key=request.private_key,
        network=request.network,
        testnet=request.testnet,
        gas_price_gwei=request.gas_price_gwei
    )
    
    return {
        "message": "Payment processor deployment started",
        "deployment_id": deployment_id,
        "status": "pending"
    }

@router.get("/status/{deployment_id}")
async def get_deployment_status(
    deployment_id: str,
    username: str = Depends(get_current_user)
):
    """Get the status of a contract deployment"""
    if deployment_id not in deployment_statuses:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    return deployment_statuses[deployment_id]

@router.post("/processor/configure")
async def configure_processor(
    request: ConfigureProcessorRequest,
    username: str = Depends(get_current_user)
):
    """Configure the payment processor to support a token"""
    try:
        # Get blockchain service
        blockchain_service = get_blockchain_service(
            network=request.network,
            testnet=request.testnet
        )
        
        # Get processor contract instance
        processor_contract = blockchain_service.get_payment_processor_contract(
            contract_address=request.processor_address
        )
        
        # Convert addresses to checksum format
        web3 = blockchain_service.web3
        checksum_processor = web3.toChecksumAddress(request.processor_address)
        checksum_token = web3.toChecksumAddress(request.token_address)
        checksum_deployer = web3.toChecksumAddress(request.deployer_address)
        
        # Check if the deployer is the owner of the contract
        try:
            owner = processor_contract.functions.owner().call()
            if owner.lower() != checksum_deployer.lower():
                raise HTTPException(
                    status_code=403,
                    detail="Only the contract owner can configure the processor"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error checking contract ownership: {str(e)}"
            )
        
        # Get gas price
        gas_price = web3.eth.gas_price
        if request.gas_price_gwei:
            gas_price = web3.toWei(request.gas_price_gwei, "gwei")
        
        # Build transaction to set token support
        nonce = web3.eth.get_transaction_count(checksum_deployer)
        tx = processor_contract.functions.setTokenSupport(
            checksum_token,
            request.is_supported
        ).buildTransaction({
            'from': checksum_deployer,
            'nonce': nonce,
            'gas': 100000,  # Standard function call
            'gasPrice': gas_price,
            'chainId': web3.eth.chain_id
        })
        
        # Sign and send transaction
        signed_tx = web3.eth.account.sign_transaction(tx, request.private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for transaction receipt
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        # Get token symbol
        try:
            token_contract = blockchain_service.get_erc20_contract(checksum_token)
            symbol = token_contract.functions.symbol().call()
        except:
            symbol = "Unknown"
        
        # Return transaction details
        return {
            'message': f"Token {symbol} {'added to' if request.is_supported else 'removed from'} supported tokens",
            'transaction_hash': tx_hash.hex(),
            'processor_address': checksum_processor,
            'token_address': checksum_token,
            'token_symbol': symbol,
            'is_supported': request.is_supported,
            'status': 'success' if receipt.status == 1 else 'failed',
            'block_number': receipt.blockNumber,
            'gas_used': receipt.gasUsed
        }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error configuring payment processor: {str(e)}"
        ) 