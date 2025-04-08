from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from app.database import get_db
from app.models import User, Wallet
from pydantic import BaseModel, EmailStr
import bcrypt
from jose import jwt
from datetime import datetime, timedelta
from app.dependencies.auth import get_current_user
from app.config import AppConfig
from typing import Optional, Dict, Any

router = APIRouter()

# Get configuration
config = AppConfig()
SECRET_KEY = config.auth.secret_key
ALGORITHM = config.auth.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = config.auth.access_token_expire_minutes

class UserCreate(BaseModel):
    username: str
    password: str
    wallet_address: str
    email: str  # Added email as a required field

@router.post("/register/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Use a more direct query approach that's safer for schema migrations
    result = db.execute(text(f"SELECT id FROM users WHERE username = :username"), {"username": user.username}).first()
    if result:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email already exists - use raw SQL to avoid ORM schema issues
    result = db.execute(text(f"SELECT id FROM users WHERE email = :email"), {"email": user.email}).first()
    if result:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    try:
        # Use direct SQL insert instead of ORM to avoid schema mismatches
        db.execute(
            text("""
                INSERT INTO users (username, hashed_password, wallet_address, email, role, is_active) 
                VALUES (:username, :hashed_password, :wallet_address, :email, :role, :is_active)
            """),
            {
                "username": user.username,
                "hashed_password": hashed_password,
                "wallet_address": user.wallet_address,
                "email": user.email,
                "role": "user",
                "is_active": True
            }
        )
        db.commit()
        
        # Get the newly created user ID
        new_user = db.execute(text(f"SELECT id FROM users WHERE username = :username"), {"username": user.username}).first()
        user_id = new_user[0]
        
        # Create a wallet for the new user
        db.execute(
            text("""
                INSERT INTO wallets (user_id, fiat_balance, stablecoin_balance, currency) 
                VALUES (:user_id, :fiat_balance, :stablecoin_balance, :currency)
            """),
            {
                "user_id": user_id,
                "fiat_balance": 0.0,
                "stablecoin_balance": 0.0,
                "currency": "USD"
            }
        )
        db.commit()
    except Exception as e:
        db.rollback()
        # If we get a database error, show detailed error message
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {"message": "User registered successfully!", "user_id": user_id}

@router.get("/")
def read_users(db: Session = Depends(get_db)):
    users = db.execute(text("SELECT id, username, wallet_address, email FROM users")).fetchall()
    return [{"id": user[0], "username": user[1], "wallet_address": user[2], "email": user[3]} for user in users]

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login/", response_model=Token)
def login(user: LoginRequest, db: Session = Depends(get_db)):
    # Get user using raw SQL to avoid ORM schema issues
    result = db.execute(
        text(f"SELECT id, username, hashed_password FROM users WHERE username = :username"), 
        {"username": user.username}
    ).first()
    if not result:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    user_id, username, hashed_password = result
    
    if not bcrypt.checkpw(user.password.encode("utf-8"), hashed_password.encode("utf-8")):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
    
@router.get("/user/")
def get_user_details(username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get user using raw SQL to avoid ORM schema issues
    result = db.execute(
        text(f"SELECT id, username, wallet_address, email FROM users WHERE username = :username"),
        {"username": username}
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id, username, wallet_address, email = result
    
    # Try to get user metadata if it exists
    try:
        metadata = db.execute(
            text("SELECT profile_data FROM user_metadata WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).first()
        
        profile_data = metadata[0] if metadata else {}
    except:
        profile_data = {}
    
    # Get wallet details
    wallet = db.execute(
        text("SELECT currency, country_code FROM wallets WHERE user_id = :user_id"),
        {"user_id": user_id}
    ).first()
    
    currency = wallet[0] if wallet else "USD"
    country_code = wallet[1] if wallet and len(wallet) > 1 else None
    
    return {
        "id": user_id,
        "username": username,
        "email": email,
        "wallet_address": wallet_address,
        "currency": currency,
        "country_code": country_code,
        "profile": profile_data
    }

class UserMetadata(BaseModel):
    user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    id_number: Optional[str] = None
    id_type: Optional[str] = None
    document_type: Optional[str] = None
    document_number: Optional[str] = None
    profile_data: Optional[Dict[str, Any]] = None

@router.post("/{user_id}/metadata")
def create_user_metadata(user_id: int, metadata: UserMetadata, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    # Check if the user exists
    user = db.execute(text("SELECT id, username FROM users WHERE id = :user_id"), {"user_id": user_id}).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check permissions: only admins or the user themselves can update their metadata
    current_user_data = db.execute(
        text("SELECT id, role FROM users WHERE username = :username"),
        {"username": current_user}
    ).first()
    
    if not current_user_data:
        raise HTTPException(status_code=404, detail="Current user not found")
    
    current_user_id, role = current_user_data
    if current_user_id != user_id and role != "admin":
        raise HTTPException(status_code=403, detail="You don't have permission to update this user's information")
    
    try:
        # Check if metadata already exists
        existing = db.execute(
            text("SELECT id FROM user_metadata WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).first()
        
        if existing:
            # Update existing metadata
            db.execute(
                text("""
                    UPDATE user_metadata SET 
                    first_name = :first_name,
                    last_name = :last_name, 
                    date_of_birth = :date_of_birth,
                    country = :country,
                    country_code = :country_code,
                    id_number = :id_number,
                    id_type = :id_type,
                    document_type = :document_type,
                    document_number = :document_number,
                    profile_data = :profile_data,
                    updated_at = :updated_at
                    WHERE user_id = :user_id
                """),
                {
                    "user_id": user_id,
                    "first_name": metadata.first_name,
                    "last_name": metadata.last_name,
                    "date_of_birth": metadata.date_of_birth,
                    "country": metadata.country,
                    "country_code": metadata.country_code,
                    "id_number": metadata.id_number,
                    "id_type": metadata.id_type,
                    "document_type": metadata.document_type,
                    "document_number": metadata.document_number,
                    "profile_data": metadata.profile_data,
                    "updated_at": datetime.utcnow()
                }
            )
        else:
            # Create new metadata
            db.execute(
                text("""
                    INSERT INTO user_metadata 
                    (user_id, first_name, last_name, date_of_birth, country, country_code, 
                    id_number, id_type, document_type, document_number, profile_data, created_at) 
                    VALUES 
                    (:user_id, :first_name, :last_name, :date_of_birth, :country, :country_code,
                    :id_number, :id_type, :document_type, :document_number, :profile_data, :created_at)
                """),
                {
                    "user_id": user_id,
                    "first_name": metadata.first_name,
                    "last_name": metadata.last_name,
                    "date_of_birth": metadata.date_of_birth,
                    "country": metadata.country,
                    "country_code": metadata.country_code,
                    "id_number": metadata.id_number,
                    "id_type": metadata.id_type,
                    "document_type": metadata.document_type,
                    "document_number": metadata.document_number,
                    "profile_data": metadata.profile_data,
                    "created_at": datetime.utcnow()
                }
            )
        
        db.commit()
        return {"message": "User metadata saved successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving user metadata: {str(e)}")

@router.get("/{user_id}/metadata")
def get_user_metadata(user_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    # Check permissions: only admins or the user themselves can view their metadata
    current_user_data = db.execute(
        text("SELECT id, role FROM users WHERE username = :username"),
        {"username": current_user}
    ).first()
    
    if not current_user_data:
        raise HTTPException(status_code=404, detail="Current user not found")
    
    current_user_id, role = current_user_data
    if current_user_id != user_id and role != "admin":
        raise HTTPException(status_code=403, detail="You don't have permission to view this user's information")
    
    metadata = db.execute(
        text("""
            SELECT 
                user_id, first_name, last_name, date_of_birth, country, country_code,
                id_number, id_type, document_type, document_number, profile_data
            FROM user_metadata 
            WHERE user_id = :user_id
        """),
        {"user_id": user_id}
    ).first()
    
    if not metadata:
        raise HTTPException(status_code=404, detail="User metadata not found")
    
    # Convert to dict
    metadata_dict = {
        "user_id": metadata[0],
        "first_name": metadata[1],
        "last_name": metadata[2],
        "date_of_birth": metadata[3],
        "country": metadata[4],
        "country_code": metadata[5],
        "id_number": metadata[6],
        "id_type": metadata[7],
        "document_type": metadata[8],
        "document_number": metadata[9],
        "profile_data": metadata[10]
    }
    
    return metadata_dict

@router.get("/verify-identity/{user_id}")
def verify_user_identity(user_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    """
    Endpoint to check if a user's identity has been verified.
    This would typically connect to a KYC provider in a production environment.
    """
    # Check permissions (admin only)
    admin_check = db.execute(
        text("SELECT role FROM users WHERE username = :username"),
        {"username": current_user}
    ).first()
    
    if not admin_check or admin_check[0] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get user metadata
    metadata = db.execute(
        text("""
            SELECT id_number, id_type, document_type, document_number
            FROM user_metadata 
            WHERE user_id = :user_id
        """),
        {"user_id": user_id}
    ).first()
    
    if not metadata or not metadata[0]:
        return {
            "user_id": user_id,
            "verified": False,
            "message": "User identity information not found"
        }
    
    # In a real system, this would call an external KYC service
    # For demo purposes, we'll simulate verification success
    try:
        # Update verification status in database
        db.execute(
            text("""
                UPDATE user_metadata
                SET verification_status = 'verified',
                    verified_at = :verified_at
                WHERE user_id = :user_id
            """),
            {
                "user_id": user_id,
                "verified_at": datetime.utcnow()
            }
        )
        db.commit()
        
        return {
            "user_id": user_id,
            "verified": True,
            "message": "User identity verified successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating verification status: {str(e)}")
