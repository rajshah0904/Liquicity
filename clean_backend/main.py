from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import get_db, test_connection
from .routers.onboarding import router as onboard_router
from .routers.user_check import router as user_router
from .routers.kyc import router as kyc_router
from .routers.user_profile import router as profile_router
from .routers.wallet import router as wallet_router
from .routers.card import router as card_router
from .routers.external_accounts import router as external_router
from .routers.virtual_accounts import router as va_router
from .routers.webhooks import router as webhook_router
from .routers.transfer import router as transfer_router, public_router as transfer_public_router
from .routers.crypto import router as crypto_router

app = FastAPI(title="Liquicity Clean API")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "liquicity-api"}

@app.get("/health/db")
async def database_health_check(db: Session = Depends(get_db)):
    """Database health check endpoint"""
    try:
        # Test database connection
        if test_connection():
            return {"status": "healthy", "database": "connected"}
        else:
            return {"status": "unhealthy", "database": "disconnected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "error", "message": str(e)}

# Include all routers
app.include_router(onboard_router) 
app.include_router(user_router)
app.include_router(kyc_router)
app.include_router(profile_router)
app.include_router(wallet_router)
app.include_router(card_router)
app.include_router(external_router)
app.include_router(va_router)
app.include_router(webhook_router)
app.include_router(transfer_router)
app.include_router(transfer_public_router)
app.include_router(crypto_router)

# --- CORS so that http://localhost:3000 front-end can call the API ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Location"],
) 