from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import user, wallet, payment
from app.database import engine, Base, get_db
from app.dependencies.auth import get_current_user
from sqlalchemy import text
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Create static directory for avatars if it doesn't exist
static_dir = "static"
avatars_dir = os.path.join(static_dir, "avatars")
if not os.path.exists(avatars_dir):
    os.makedirs(avatars_dir, exist_ok=True)

app = FastAPI(title="Liquicity API", version="0.1.0")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only the essential routers
app.include_router(user, prefix="/user", tags=["users"])
app.include_router(wallet, prefix="/wallet", tags=["wallets"])
app.include_router(payment, prefix="/payment", tags=["payments"])

@app.get("/", tags=["status"])
async def root():
    """API root endpoint"""
    return {"message": "Welcome to Liquicity API", "status": "online"}

@app.get("/health", tags=["status"])
async def health_check(db=Depends(get_db)):
    """Check API and database health"""
    try:
        # Try to execute a simple query
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "version": "0.1.0"
    }
