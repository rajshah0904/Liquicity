from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import BlockchainWallet, BlockchainTransaction, User
from app.blockchain.wallet import WalletManager
from app.dependencies.auth import get_current_user
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
import re
from app.utils.blockchain import get_blockchain_service

router = APIRouter()

class WalletCreate(BaseModel):
    """Request model for creating a blockchain wallet"""
    user_id: int
    name: str
    chain: str = "ethereum"  # ethereum, polygon, avalanche, etc.

class WalletResponse(BaseModel):
    id: int
    name: str
    address: str
    chain: str
    wallet_type: str
    is_active: bool
    user_id: Optional[int] = None
    team_id: Optional[int] = None
    safe_address: Optional[str] = None
    safe_threshold: Optional[int] = None

class SafeWalletCreate(BaseModel):
    name: str
    chain: str = "ethereum"
    owner_addresses: List[str]
    threshold: int
    team_id: Optional[int] = None

class TokenTransferRequest(BaseModel):
    """Request model for transferring tokens"""
    from_address: str
    to_address: str
    token_address: str
    amount: float
    private_key: str  # WARNING: Private keys should be handled securely!
    gas_price_gwei: Optional[int] = None
    
    @validator('from_address', 'to_address', 'token_address')
    def validate_ethereum_address(cls, v):
        if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
            raise ValueError(f"Invalid Ethereum address format: {v}")
        return v
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v

class SmartContractPaymentRequest(BaseModel):
    """Request model for processing a payment via smart contract"""
    processor_address: str
    token_address: str
    from_address: str
    to_address: str
    amount: float
    reference: str
    private_key: str  # WARNING: Private keys should be handled securely!
    gas_price_gwei: Optional[int] = None
    network: str = "ethereum"
    testnet: bool = False
    
    @validator('processor_address', 'token_address', 'from_address', 'to_address')
    def validate_ethereum_address(cls, v):
        if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
            raise ValueError(f"Invalid Ethereum address format: {v}")
        return v
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v

# Wallet Management

@router.post("/wallet/create")
def create_blockchain_wallet(wallet: WalletCreate, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """Create a new blockchain wallet"""
    # Check if user exists
    user = db.query(User).filter(User.id == wallet.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create blockchain wallet
    blockchain_service = get_blockchain_service(network=wallet.chain, testnet=True)
    
    try:
        # Generate a new account
        account = blockchain_service.create_account()
        
        # Store in database
        new_wallet = BlockchainWallet(
            address=account["address"],
            chain=wallet.chain,
            wallet_type="eoa",  # Externally Owned Account
            name=wallet.name,
            user_id=wallet.user_id,
            is_active=True,
            meta_data={"created_at": "now"}
        )
        
        db.add(new_wallet)
        db.commit()
        db.refresh(new_wallet)
        
        # Return wallet info (but NEVER return private keys in API responses!)
        return {
            "message": "Blockchain wallet created successfully",
            "wallet": {
                "id": new_wallet.id,
                "address": new_wallet.address,
                "chain": new_wallet.chain,
                "name": new_wallet.name,
                "wallet_type": new_wallet.wallet_type
            },
            # WARNING: In a production app, you would NEVER return this.
            # Either store encrypted in a secure vault or have the user manage it themselves.
            "private_key": account["private_key"]
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating blockchain wallet: {str(e)}")

@router.get("/wallet/{wallet_id}")
def get_blockchain_wallet(wallet_id: int, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """Get blockchain wallet details"""
    wallet = db.query(BlockchainWallet).filter(BlockchainWallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Blockchain wallet not found")
    
    # Get balance
    try:
        blockchain_service = get_blockchain_service(network=wallet.chain, testnet=True)
        eth_balance = blockchain_service.get_eth_balance(wallet.address)
        
        # For demo purposes, get USDT balance on Ethereum
        # In production, you'd support multiple tokens based on user preferences
        usdt_balance = 0
        try:
            if wallet.chain == "ethereum":
                # Ethereum Mainnet USDT
                usdt_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
                usdt_balance = blockchain_service.get_token_balance(usdt_address, wallet.address)
        except Exception:
            pass  # Ignore token balance errors
        
        return {
            "id": wallet.id,
            "address": wallet.address,
            "chain": wallet.chain,
            "name": wallet.name,
            "wallet_type": wallet.wallet_type,
            "balances": {
                "native": eth_balance,
                "usdt": usdt_balance
            },
            "is_active": wallet.is_active,
            "created_at": wallet.created_at
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching wallet details: {str(e)}")

@router.get("/wallets/user/{user_id}")
def get_user_blockchain_wallets(user_id: int, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    """Get all blockchain wallets for a user"""
    wallets = db.query(BlockchainWallet).filter(BlockchainWallet.user_id == user_id).all()
    return wallets

@router.post("/token/transfer")
def transfer_token(request: TokenTransferRequest, username: str = Depends(get_current_user)):
    """Transfer ERC20 tokens from one address to another"""
    try:
        # Default to Ethereum mainnet
        blockchain_service = get_blockchain_service(network="ethereum", testnet=False)
        
        # Process token transfer
        result = blockchain_service.send_token(
            token_address=request.token_address,
            from_address=request.from_address,
            to_address=request.to_address,
            amount=request.amount,
            private_key=request.private_key,
            gas_price_gwei=request.gas_price_gwei
        )
        
        return {
            "message": "Token transfer successful",
            "transaction": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token transfer failed: {str(e)}")

@router.post("/payment/process")
def process_contract_payment(request: SmartContractPaymentRequest, username: str = Depends(get_current_user)):
    """Process a payment through the TerraFlow payment processor smart contract"""
    try:
        # Get blockchain service for the specified network
        blockchain_service = get_blockchain_service(network=request.network, testnet=request.testnet)
        
        # Process payment through the contract
        result = blockchain_service.process_payment(
            processor_address=request.processor_address,
            token_address=request.token_address,
            sender_address=request.from_address,
            recipient_address=request.to_address,
            amount=request.amount,
            reference=request.reference,
            private_key=request.private_key,
            gas_price_gwei=request.gas_price_gwei
        )
        
        return {
            "message": "Smart contract payment processed successfully",
            "transaction": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart contract payment failed: {str(e)}")

@router.get("/transaction/{tx_hash}")
def get_transaction_status(tx_hash: str, chain: str = "ethereum", username: str = Depends(get_current_user)):
    """Get the status of a blockchain transaction"""
    try:
        # Get blockchain service for the specified chain
        blockchain_service = get_blockchain_service(network=chain, testnet=True)
        
        # Get transaction receipt
        receipt = blockchain_service.web3.eth.get_transaction_receipt(tx_hash)
        
        # Get transaction details
        tx = blockchain_service.web3.eth.get_transaction(tx_hash)
        
        return {
            "transaction_hash": tx_hash,
            "status": "success" if receipt.status == 1 else "failed",
            "block_number": receipt.blockNumber,
            "from": receipt.get("from", tx.get("from")),
            "to": receipt.get("to", tx.get("to")),
            "gas_used": receipt.gasUsed,
            "gas_price": blockchain_service.web3.fromWei(tx.gasPrice, "gwei"),
            "transaction_fee_eth": blockchain_service.web3.fromWei(receipt.gasUsed * tx.gasPrice, "ether")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting transaction status: {str(e)}")

@router.post("/wallets/", response_model=WalletResponse)
def create_wallet(
    wallet: WalletCreate, 
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Create a new blockchain wallet for the current user"""
    # Get the current user
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Initialize wallet manager
    wallet_manager = WalletManager(chain=wallet.chain)
    
    # Create wallet based on type
    if wallet.wallet_type == "eoa":
        address, private_key = wallet_manager.create_eoa_wallet()
        
        # Store in database
        db_wallet = wallet_manager.record_wallet_in_db(
            db=db,
            address=address,
            wallet_type=wallet.wallet_type,
            name=wallet.name,
            user_id=user.id,
            team_id=wallet.team_id,
            metadata={"creation_date": "NOW()"}  # Example metadata
        )
        
        # The private key should be returned ONLY ONCE and then stored securely by the client
        # In a production environment, use a secure vault like AWS KMS or HashiCorp Vault
        return {
            **db_wallet.__dict__,
            "private_key": private_key  # WARNING: Only return once!
        }
    
    else:
        raise HTTPException(status_code=400, detail=f"Wallet type {wallet.wallet_type} not supported directly. Use /wallets/safe for multisig wallets")

@router.post("/wallets/safe/", response_model=WalletResponse)
def create_safe_wallet(
    safe_wallet: SafeWalletCreate,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Create a Gnosis Safe multi-signature wallet"""
    # Get the current user
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate threshold
    if safe_wallet.threshold <= 0 or safe_wallet.threshold > len(safe_wallet.owner_addresses):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid threshold: must be between 1 and {len(safe_wallet.owner_addresses)}"
        )
    
    # Initialize wallet manager
    wallet_manager = WalletManager(chain=safe_wallet.chain)
    
    # Create the Safe
    safe_result = wallet_manager.create_gnosis_safe(
        owners=safe_wallet.owner_addresses,
        threshold=safe_wallet.threshold
    )
    
    # Record in database
    db_wallet = wallet_manager.record_wallet_in_db(
        db=db,
        address=safe_result["safe_address"],
        wallet_type="gnosis_safe",
        name=safe_wallet.name,
        user_id=user.id,
        team_id=safe_wallet.team_id,
        safe_address=safe_result["safe_address"],
        safe_owners=safe_wallet.owner_addresses,
        safe_threshold=safe_wallet.threshold,
        metadata={
            "creation_date": "NOW()",
            "deployment_transaction": safe_result["deployment_transaction"]
        }
    )
    
    return db_wallet

@router.get("/wallets/", response_model=List[WalletResponse])
def get_wallets(
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Get all wallets for the current user"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    wallets = db.query(BlockchainWallet).filter(BlockchainWallet.user_id == user.id).all()
    return wallets

@router.get("/wallets/{wallet_id}", response_model=WalletResponse)
def get_wallet(
    wallet_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Get a specific wallet by ID"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    wallet = db.query(BlockchainWallet).filter(
        BlockchainWallet.id == wallet_id,
        BlockchainWallet.user_id == user.id
    ).first()
    
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    return wallet

@router.get("/transactions/{wallet_id}")
def get_wallet_transactions(
    wallet_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """Get all transactions for a specific wallet"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Ensure wallet belongs to user
    wallet = db.query(BlockchainWallet).filter(
        BlockchainWallet.id == wallet_id,
        BlockchainWallet.user_id == user.id
    ).first()
    
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found or not authorized")
    
    # Get transactions
    transactions = db.query(BlockchainTransaction).filter(
        BlockchainTransaction.wallet_id == wallet_id
    ).all()
    
    return transactions 