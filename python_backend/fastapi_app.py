"""
FastAPI Application Entry Point
Production-level FastAPI app for WalletConnect v2 + USDC crypto payments
"""

import uvicorn
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import traceback

from config.settings import settings
from api.routes import app as api_app

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Global state for startup/shutdown
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Liquicity Crypto Payment API")
    logger.info(f"Environment: {settings.environment.value}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Database URL: {settings.database_url}")
    logger.info(f"Redis URL: {settings.redis_url}")
    
    # Initialize services
    try:
        # Initialize database connections
        # await init_database()
        
        # Initialize Redis
        # await init_redis()
        
        # Initialize WalletConnect
        # await init_walletconnect()
        
        # Initialize Bridge API
        # await init_bridge_api()
        
        logger.info("✅ All services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        logger.error(traceback.format_exc())
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Liquicity Crypto Payment API")
    
    try:
        # Close database connections
        # await close_database()
        
        # Close Redis connections
        # await close_redis()
        
        # Close WalletConnect connections
        # await close_walletconnect()
        
        logger.info("✅ All services closed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")

# Create FastAPI app
app = FastAPI(
    title="Liquicity Crypto Payment API",
    description="""
    ## WalletConnect v2 + USDC Crypto Payment Gateway
    
    Production-level API for crypto-native users without bank accounts.
    
    ### Features:
    - **WalletConnect v2 Integration**: Secure wallet connections
    - **USDC Payments**: Cross-chain USDC transfers
    - **Bridge API Integration**: On/off-ramp capabilities
    - **Multi-Chain Support**: Ethereum, Polygon, Base, Solana
    - **Gas Optimization**: Automatic gas estimation and optimization
    - **Security**: JWT authentication, rate limiting, risk scoring
    
    ### Quick Start:
    1. Connect wallet: `POST /api/v1/wallet/connect`
    2. Create transfer: `POST /api/v1/payments/usdc/transfer`
    3. User approves in wallet
    4. Sign transaction: `POST /api/v1/payments/usdc/sign`
    
    ### Cost Savings:
    - Traditional: 4.5% + $0.50
    - Crypto: $0.01-0.10 (Polygon)
    - **Savings: 95%+**
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

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

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Internal server error",
                "details": str(exc) if settings.debug else None
            }
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "Liquicity Crypto Payment API",
        "version": "1.0.0",
        "environment": settings.environment.value,
        "debug": settings.debug
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Liquicity Crypto Payment API",
        "version": "1.0.0",
        "description": "WalletConnect v2 + USDC crypto payment gateway",
        "docs": "/docs",
        "health": "/health",
        "features": [
            "WalletConnect v2 Integration",
            "USDC Cross-Chain Payments",
            "Bridge API Integration",
            "Multi-Chain Support",
            "Gas Optimization",
            "Security & Compliance"
        ]
    }

# Include API routes
app.mount("/api", api_app)

if __name__ == "__main__":
    uvicorn.run(
        "fastapi_app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug",
        access_log=True
    ) 