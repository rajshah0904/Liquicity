import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from clean_backend.routers.velafi import (
    router as velafi_router,
)
from clean_backend.routers.velafi import (
    webhook_router as velafi_webhook_router,
)
from clean_backend.services.velafi_monitor import run_monitor
from VelaFi.onramp import router as onramp_router

from .routers.card import router as card_router
from .routers.crypto import router as crypto_router
from .routers.external_accounts import router as external_router
from .routers.kyc import router as kyc_router
from .routers.onboarding import router as onboard_router
from .routers.transfer import public_router as transfer_public_router
from .routers.transfer import router as transfer_router
from .routers.user_check import router as user_router
from .routers.user_profile import router as profile_router
from .routers.virtual_accounts import router as va_router
from .routers.wallet import router as wallet_router
from .routers.webhooks import router as webhook_router

app = FastAPI(title="Liquicity Clean API")
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

# VelaFi on-ramp routes
app.include_router(onramp_router)
app.include_router(velafi_router)
app.include_router(velafi_webhook_router)

# Start background tasks
@app.on_event("startup")
async def startup_event():
    # Start VelaFi monitor with 1-minute polling interval
    asyncio.create_task(run_monitor(poll_interval=60))

# --- CORS so that http://localhost:3000 front-end can call the API ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Location"],
)