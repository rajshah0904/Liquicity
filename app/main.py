from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import user, trade, transaction, wallet, blockchain, compliance, payment, deployment, stripe

app = FastAPI(title="TerraFlow", 
              description="A cross-currency payment system using stablecoins",
              version="1.0.0")

# Configure CORS properly for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include the routers with appropriate prefixes and tags.
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(trade.router, prefix="/trade", tags=["trade"])
app.include_router(transaction.router, prefix="/transaction", tags=["transaction"])
app.include_router(wallet.router, prefix="/wallet", tags=["wallet"])
app.include_router(blockchain.router, prefix="/blockchain", tags=["blockchain"])
app.include_router(compliance.router, prefix="/compliance", tags=["compliance"])
app.include_router(payment.router, prefix="/payment", tags=["payment"])
app.include_router(deployment.router, prefix="/deployment", tags=["deployment"])
app.include_router(stripe.router, prefix="/payment/stripe", tags=["stripe"])

# Temporarily commented out AI router
# app.include_router(ai.router, prefix="/ai", tags=["ai"])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to TerraFlow!",
        "description": "A cross-currency payment system using stablecoins as an intermediary",
        "endpoints": {
            "user": "/user - User management endpoints",
            "wallet": "/wallet - Wallet management endpoints",
            "transaction": "/transaction - Process cross-currency transactions",
            "trade": "/trade - Legacy trade endpoints",
            "blockchain": "/blockchain - Blockchain wallet endpoints",
            "compliance": "/compliance - KYC and AML compliance endpoints",
            "payment": "/payment - Deposit, withdrawal, and transfer endpoints",
            "deployment": "/deployment - Smart contract deployment endpoints",
            # Temporarily commented out
            # "ai": "/ai - AI agent endpoints"
        }
    }
