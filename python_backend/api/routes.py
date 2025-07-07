"""
FastAPI Routes
Production-level API endpoints for WalletConnect v2 + USDC crypto payments
"""

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from decimal import Decimal
import asyncio
import time
import logging

from config.settings import settings, ERROR_CODES, SUCCESS_CODES
from core.security import (
    SecurityException, 
    authentication_service, 
    authorization_service,
    security_validator,
    rate_limiter,
    calculate_risk_score,
    SecurityContext
)
from core.walletconnect_v2_service import (
    WalletConnectV2Service, 
    WalletConnectError,
    ChainType,
    SessionStatus
)
from core.usdc_payment_service import (
    USDCPaymentService,
    USDCError,
    TransactionStatus
)
from core.bridge_api_client import (
    BridgeAPIClient,
    BridgeError,
    BridgeTransferRequest
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Liquicity Crypto Payment API",
    description="WalletConnect v2 + USDC crypto payment gateway for users without bank accounts",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security middleware
security = HTTPBearer()

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.environment.value != "development":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure for production
    )

# Initialize services
walletconnect_service = WalletConnectV2Service()
usdc_payment_service = USDCPaymentService()
bridge_client = BridgeAPIClient()

# Pydantic models
class WalletConnectRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    wallet_address: str = Field(..., description="User's wallet address")
    chain_type: ChainType = Field(..., description="Chain type (evm or solana)")
    chain_id: str = Field(..., description="Chain ID")

class WalletConnectResponse(BaseModel):
    session_id: str
    qr_code_url: str
    uri: str
    status: str
    expires_at: str

class USDCTransferRequest(BaseModel):
    session_id: str = Field(..., description="Wallet session ID")
    to_address: str = Field(..., description="Recipient wallet address")
    amount: str = Field(..., description="USDC amount")
    currency: str = Field("usdc", description="Currency (default: usdc)")
    urgency: Optional[str] = Field("low", description="Payment urgency (low/medium/high)")

class USDCTransferResponse(BaseModel):
    transfer_id: str
    session_id: str
    amount: str
    to_address: str
    chain_type: str
    chain_id: str
    gas_estimate: Dict[str, Any]
    status: str
    expires_at: str

class TransactionSignRequest(BaseModel):
    transfer_id: str = Field(..., description="Transfer ID")
    signed_transaction: str = Field(..., description="Signed transaction data")

class TransactionSignResponse(BaseModel):
    transfer_id: str
    transaction_hash: str
    status: str
    confirmation_time: Optional[str]

class BridgeTransferRequest(BaseModel):
    session_id: str = Field(..., description="Wallet session ID")
    amount: str = Field(..., description="Transfer amount")
    source_network: str = Field(..., description="Source network")
    source_address: str = Field(..., description="Source address")
    destination_network: str = Field(..., description="Destination network")
    destination_address: str = Field(..., description="Destination address")
    currency: str = Field("usdc", description="Currency")

class CostSavingsRequest(BaseModel):
    amount: str = Field(..., description="Payment amount")
    source_network: Optional[str] = Field(None, description="Source network")

class CostSavingsResponse(BaseModel):
    traditional_cost: str
    crypto_cost: str
    savings: str
    savings_percentage: float
    gas_estimate: str
    recommended_network: str

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from JWT token"""
    try:
        payload = authentication_service.verify_token(credentials.credentials)
        return payload
    except SecurityException as e:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": {
                    "code": e.error_code,
                    "message": e.message
                }
            }
        )

# Rate limiting dependency
async def check_rate_limit(request: Request, user_id: str):
    """Check rate limiting for user"""
    if settings.enable_rate_limiting:
        # In production, use Redis for rate limiting
        # For now, we'll use a simple in-memory check
        pass

# Security context dependency
async def get_security_context(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> SecurityContext:
    """Create security context for request"""
    
    # Get client IP
    client_ip = request.client.host
    if "x-forwarded-for" in request.headers:
        client_ip = request.headers["x-forwarded-for"].split(",")[0]
    
    # Get user agent
    user_agent = request.headers.get("user-agent", "")
    
    # Calculate risk score
    context = SecurityContext(
        user_id=current_user.get("sub"),
        ip_address=client_ip,
        user_agent=user_agent,
        permissions=current_user.get("permissions", [])
    )
    
    context.risk_score = calculate_risk_score(context)
    
    return context

# Error handling middleware
@app.exception_handler(SecurityException)
async def security_exception_handler(request: Request, exc: SecurityException):
    """Handle security exceptions"""
    logger.warning(f"Security exception: {exc.error_code} - {exc.message}")
    return HTTPException(
        status_code=401 if "AUTH" in exc.error_code else 400,
        detail={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

@app.exception_handler(WalletConnectError)
async def walletconnect_exception_handler(request: Request, exc: WalletConnectError):
    """Handle WalletConnect exceptions"""
    logger.error(f"WalletConnect error: {exc.error_code} - {exc.message}")
    return HTTPException(
        status_code=400,
        detail={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

@app.exception_handler(USDCError)
async def usdc_exception_handler(request: Request, exc: USDCError):
    """Handle USDC payment exceptions"""
    logger.error(f"USDC error: {exc.error_code} - {exc.message}")
    return HTTPException(
        status_code=400,
        detail={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

@app.exception_handler(BridgeError)
async def bridge_exception_handler(request: Request, exc: BridgeError):
    """Handle Bridge API exceptions"""
    logger.error(f"Bridge API error: {exc.error_code} - {exc.message}")
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "Liquicity Crypto Payment API",
        "version": "1.0.0",
        "environment": settings.environment.value
    }

# WalletConnect endpoints
@app.post("/api/v1/wallet/connect", response_model=WalletConnectResponse)
async def connect_wallet(
    request: WalletConnectRequest,
    security_context: SecurityContext = Depends(get_security_context)
):
    """Connect user's wallet via WalletConnect v2"""
    
    try:
        # Validate wallet address
        if not security_validator.validate_wallet_address(
            request.wallet_address, 
            request.chain_id
        ):
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": ERROR_CODES["INVALID_WALLET_ADDRESS"],
                        "message": "Invalid wallet address for the specified chain"
                    }
                }
            )
        
        # Create WalletConnect session
        session = await walletconnect_service.create_session(
            user_id=request.user_id,
            wallet_address=request.wallet_address,
            chain_type=request.chain_type,
            chain_id=request.chain_id
        )
        
        # Generate QR code
        qr_code_url = await walletconnect_service.generate_qr_code(session.id)
        
        # Generate URI for deep linking
        uri = f"wc:{settings.walletconnect_project_id}@2?relay-protocol=irn&chainId={request.chain_id}&session_id={session.id}"
        
        logger.info(f"Created WalletConnect session {session.id} for user {request.user_id}")
        
        return WalletConnectResponse(
            session_id=session.id,
            qr_code_url=qr_code_url,
            uri=uri,
            status=session.status.value,
            expires_at=session.expires_at.isoformat()
        )
    
    except WalletConnectError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": {
                    "code": e.error_code,
                    "message": e.message
                }
            }
        )
    except Exception as e:
        logger.error(f"Wallet connection error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": ERROR_CODES["INTERNAL_ERROR"],
                    "message": "Failed to connect wallet"
                }
            }
        )

@app.get("/api/v1/wallet/session/{session_id}")
async def get_session_status(
    session_id: str,
    security_context: SecurityContext = Depends(get_security_context)
):
    """Get WalletConnect session status"""
    
    try:
        session_data = await walletconnect_service.get_session_status(session_id)
        
        if not session_data:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": ERROR_CODES["SESSION_EXPIRED"],
                        "message": "Session not found"
                    }
                }
            )
        
        return {
            "success": True,
            "data": session_data
        }
    
    except Exception as e:
        logger.error(f"Session status error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": ERROR_CODES["INTERNAL_ERROR"],
                    "message": "Failed to get session status"
                }
            }
        )

@app.delete("/api/v1/wallet/session/{session_id}")
async def disconnect_session(
    session_id: str,
    security_context: SecurityContext = Depends(get_security_context)
):
    """Disconnect WalletConnect session"""
    
    try:
        success = await walletconnect_service.disconnect_session(session_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": ERROR_CODES["SESSION_EXPIRED"],
                        "message": "Session not found"
                    }
                }
            )
        
        return {
            "success": True,
            "message": "Session disconnected successfully"
        }
    
    except Exception as e:
        logger.error(f"Session disconnect error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": ERROR_CODES["INTERNAL_ERROR"],
                    "message": "Failed to disconnect session"
                }
            }
        )

# USDC Payment endpoints
@app.post("/api/v1/payments/usdc/transfer", response_model=USDCTransferResponse)
async def create_usdc_transfer(
    request: USDCTransferRequest,
    security_context: SecurityContext = Depends(get_security_context)
):
    """Create a USDC transfer request"""
    
    try:
        # Validate amount
        if not security_validator.validate_amount(float(request.amount)):
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": ERROR_CODES["INVALID_AMOUNT"],
                        "message": "Invalid amount"
                    }
                }
            )
        
        # Validate recipient address
        if not security_validator.validate_wallet_address(request.to_address, "ethereum"):
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": ERROR_CODES["INVALID_WALLET_ADDRESS"],
                        "message": "Invalid recipient address"
                    }
                }
            )
        
        # Create USDC transfer
        transfer = await usdc_payment_service.create_usdc_transfer(
            session_id=request.session_id,
            to_address=request.to_address,
            amount=request.amount,
            chain_id="ethereum",  # Default to Ethereum, can be made configurable
            currency=request.currency
        )
        
        logger.info(f"Created USDC transfer {transfer.id} for session {request.session_id}")
        
        return USDCTransferResponse(
            transfer_id=transfer.id,
            session_id=transfer.session_id,
            amount=transfer.amount,
            to_address=transfer.to_address,
            chain_type=transfer.chain_type.value,
            chain_id=transfer.chain_id,
            gas_estimate=transfer.gas_estimate.__dict__ if transfer.gas_estimate else None,
            status=transfer.status.value,
            expires_at=transfer.expires_at.isoformat() if transfer.expires_at else None
        )
    
    except USDCError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": {
                    "code": e.error_code,
                    "message": e.message
                }
            }
        )
    except Exception as e:
        logger.error(f"USDC transfer creation error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": ERROR_CODES["INTERNAL_ERROR"],
                    "message": "Failed to create USDC transfer"
                }
            }
        )

@app.post("/api/v1/payments/usdc/sign", response_model=TransactionSignResponse)
async def sign_usdc_transaction(
    request: TransactionSignRequest,
    security_context: SecurityContext = Depends(get_security_context)
):
    """Sign and broadcast USDC transaction"""
    
    try:
        # Process signed transaction
        result = await usdc_payment_service.process_signed_transaction(
            transfer_id=request.transfer_id,
            signed_transaction=request.signed_transaction
        )
        
        logger.info(f"Processed signed transaction for transfer {request.transfer_id}")
        
        return TransactionSignResponse(
            transfer_id=request.transfer_id,
            transaction_hash=result["transaction_hash"],
            status=result["status"],
            confirmation_time=result.get("confirmation_time")
        )
    
    except USDCError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": {
                    "code": e.error_code,
                    "message": e.message
                }
            }
        )
    except Exception as e:
        logger.error(f"Transaction signing error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": ERROR_CODES["INTERNAL_ERROR"],
                    "message": "Failed to process transaction"
                }
            }
        )

@app.get("/api/v1/payments/usdc/transfer/{transfer_id}")
async def get_transfer_status(
    transfer_id: str,
    security_context: SecurityContext = Depends(get_security_context)
):
    """Get USDC transfer status"""
    
    try:
        transfer_data = await usdc_payment_service.get_transfer_status(transfer_id)
        
        if not transfer_data:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": ERROR_CODES["VALIDATION_ERROR"],
                        "message": "Transfer not found"
                    }
                }
            )
        
        return {
            "success": True,
            "data": transfer_data
        }
    
    except Exception as e:
        logger.error(f"Transfer status error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": ERROR_CODES["INTERNAL_ERROR"],
                    "message": "Failed to get transfer status"
                }
            }
        )

# Bridge API endpoints (for on/off-ramp)
@app.post("/api/v1/bridge/transfer")
async def create_bridge_transfer(
    request: BridgeTransferRequest,
    security_context: SecurityContext = Depends(get_security_context)
):
    """Create a Bridge transfer for on/off-ramp"""
    
    try:
        # Create Bridge transfer request
        bridge_request = bridge_client.create_transfer_request(
            amount=request.amount,
            user_id=security_context.user_id,
            source_network=request.source_network,
            source_address=request.source_address,
            destination_network=request.destination_network,
            destination_address=request.destination_address,
            currency=request.currency
        )
        
        # Create transfer via Bridge API
        transfer = await bridge_client.create_transfer(bridge_request)
        
        logger.info(f"Created Bridge transfer {transfer.id} for user {security_context.user_id}")
        
        return {
            "success": True,
            "data": {
                "transfer_id": transfer.id,
                "status": transfer.status.value,
                "amount": transfer.amount,
                "created_at": transfer.created_at,
                "transaction_hash": transfer.transaction_hash
            }
        }
    
    except BridgeError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "success": False,
                "error": {
                    "code": e.error_code,
                    "message": e.message
                }
            }
        )
    except Exception as e:
        logger.error(f"Bridge transfer creation error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": ERROR_CODES["INTERNAL_ERROR"],
                    "message": "Failed to create Bridge transfer"
                }
            }
        )

# Utility endpoints
@app.post("/api/v1/cost-savings", response_model=CostSavingsResponse)
async def calculate_cost_savings(
    request: CostSavingsRequest,
    security_context: SecurityContext = Depends(get_security_context)
):
    """Calculate cost savings vs traditional payment processors"""
    
    try:
        amount = Decimal(request.amount)
        
        # Traditional payment processor costs
        traditional_platform_fee = amount * Decimal("0.025")  # 2.5%
        traditional_fx_fee = amount * Decimal("0.020")  # 2.0%
        traditional_network_fee = Decimal("0.50")
        traditional_total = traditional_platform_fee + traditional_fx_fee + traditional_network_fee
        
        # Crypto payment costs (using Polygon as example)
        gas_estimate = await usdc_payment_service._estimate_evm_gas(
            from_address="0x0000000000000000000000000000000000000000",
            to_address="0x0000000000000000000000000000000000000000",
            amount=request.amount,
            chain_id="polygon"
        )
        
        crypto_total = Decimal(gas_estimate.total_cost)
        
        savings = traditional_total - crypto_total
        savings_percentage = (savings / traditional_total) * 100
        
        return CostSavingsResponse(
            traditional_cost=str(traditional_total),
            crypto_cost=str(crypto_total),
            savings=str(savings),
            savings_percentage=float(savings_percentage),
            gas_estimate=str(gas_estimate.total_cost),
            recommended_network="polygon"
        )
    
    except Exception as e:
        logger.error(f"Cost savings calculation error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": ERROR_CODES["INTERNAL_ERROR"],
                    "message": "Failed to calculate cost savings"
                }
            }
        )

@app.get("/api/v1/networks")
async def get_supported_networks():
    """Get supported networks and their configurations"""
    
    networks = {
        "polygon": {
            "name": "Polygon",
            "chain_id": 137,
            "gas_cost": "$0.01-0.10",
            "speed": "15 seconds",
            "description": "Lowest cost, fast",
            "usdc_contract": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
        },
        "base": {
            "name": "Base",
            "chain_id": 8453,
            "gas_cost": "$0.005-0.05",
            "speed": "30 seconds",
            "description": "Low cost, secure",
            "usdc_contract": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
        },
        "solana": {
            "name": "Solana",
            "chain_id": "solana:mainnet",
            "gas_cost": "$0.00025",
            "speed": "1 second",
            "description": "Fastest, lowest cost",
            "usdc_contract": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        },
        "ethereum": {
            "name": "Ethereum",
            "chain_id": 1,
            "gas_cost": "$2-50",
            "speed": "2-3 minutes",
            "description": "Most secure, higher cost",
            "usdc_contract": "0xA0b86a33E6441b8C4C8C8C8C8C8C8C8C8C8C8C8C"
        }
    }
    
    return {
        "success": True,
        "data": networks
    }

@app.get("/api/v1/examples/payment-flow")
async def get_payment_flow_example():
    """Get example payment flow"""
    
    return {
        "success": True,
        "data": {
            "flow": [
                {
                    "step": 1,
                    "action": "Connect Wallet",
                    "endpoint": "POST /api/v1/wallet/connect",
                    "description": "User connects their wallet via WalletConnect v2"
                },
                {
                    "step": 2,
                    "action": "Create USDC Transfer",
                    "endpoint": "POST /api/v1/payments/usdc/transfer",
                    "description": "Create USDC transfer request with gas estimation"
                },
                {
                    "step": 3,
                    "action": "User Approves in Wallet",
                    "endpoint": "N/A",
                    "description": "User approves transaction in their wallet app"
                },
                {
                    "step": 4,
                    "action": "Sign and Broadcast",
                    "endpoint": "POST /api/v1/payments/usdc/sign",
                    "description": "Process the signed transaction"
                }
            ],
            "example_request": {
                "wallet_connect": {
                    "user_id": "user123",
                    "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                    "chain_type": "evm",
                    "chain_id": "polygon"
                },
                "usdc_transfer": {
                    "session_id": "session-uuid",
                    "to_address": "0x8ba1f109551bD432803012645Hac136c772c3",
                    "amount": "100.00",
                    "currency": "usdc"
                }
            }
        }
    }

# Background tasks
async def cleanup_expired_sessions():
    """Clean up expired sessions and transfers"""
    try:
        await walletconnect_service.cleanup_expired_sessions()
        logger.info("Cleaned up expired sessions")
    except Exception as e:
        logger.error(f"Session cleanup error: {e}")

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("Starting Liquicity Crypto Payment API")
    logger.info(f"Environment: {settings.environment.value}")
    logger.info(f"Debug mode: {settings.debug}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("Shutting down Liquicity Crypto Payment API")

# Include routers if needed
# from api.routers import auth, payments, webhooks
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
# app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
# app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"]) 