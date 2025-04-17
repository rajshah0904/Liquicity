from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
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
import os
import shutil
import uuid
from fastapi.staticfiles import StaticFiles

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
async def login(user: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT token.
    This endpoint verifies username and password credentials and returns an access token.
    """
    try:
        # Get user using raw SQL to avoid ORM schema issues
        result = db.execute(
            text("SELECT id, username, hashed_password, role FROM users WHERE username = :username"), 
            {"username": user.username}
        ).first()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id, username, hashed_password, role = result
        
        # Verify password
        if not bcrypt.checkpw(user.password.encode("utf-8"), hashed_password.encode("utf-8")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={'sub': username, 'user_id': user_id, 'role': role}, 
            expires_delta=access_token_expires
        )
        
        print(f"User {username} (ID: {user_id}) logged in successfully")
        
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Internal server error during login: {str(e)}"
        )
    
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
        text("SELECT base_currency, country_code FROM wallets WHERE user_id = :user_id"),
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

class TestUserCreate(BaseModel):
    username: str
    password: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

@router.post("/register-test/")
def create_test_user(user: TestUserCreate, db: Session = Depends(get_db)):
    """
    Test endpoint for registering users without requiring all fields.
    For development and testing purposes only.
    """
    # Check if username already exists
    result = db.execute(text("SELECT id FROM users WHERE username = :username"), {"username": user.username}).first()
    if result:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email already exists
    result = db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": user.email}).first()
    if result:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    try:
        # Insert user with minimal information
        db.execute(
            text("""
                INSERT INTO users (username, hashed_password, email, first_name, last_name, role, is_active) 
                VALUES (:username, :hashed_password, :email, :first_name, :last_name, :role, :is_active)
            """),
            {
                "username": user.username,
                "hashed_password": hashed_password,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": "user",
                "is_active": True
            }
        )
        db.commit()
        
        # Get the newly created user ID
        new_user = db.execute(text("SELECT id FROM users WHERE username = :username"), {"username": user.username}).first()
        user_id = new_user[0]
        
        # Create a wallet for the new user with default USD
        db.execute(
            text("""
                INSERT INTO wallets (user_id, fiat_balance, stablecoin_balance, base_currency, display_currency) 
                VALUES (:user_id, :fiat_balance, :stablecoin_balance, :base_currency, :display_currency)
            """),
            {
                "user_id": user_id,
                "fiat_balance": 1000.0,  # Give them $1000 to start with
                "stablecoin_balance": 100.0,  # Give them 100 USDT
                "base_currency": "USD",
                "display_currency": "USD"
            }
        )
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {
        "message": "Test user registered successfully!",
        "user_id": user_id,
        "username": user.username,
        "note": "This user has been created with minimal information for testing purposes."
    }

@router.get("/profile/{user_id}")
def get_user_profile(user_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    """Get user profile by ID"""
    # Get user using raw SQL
    result = db.execute(
        text("SELECT id, username, wallet_address, email FROM users WHERE id = :user_id"),
        {"user_id": user_id}
    ).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id, username, wallet_address, email = result
    
    return {
        "id": user_id,
        "username": username,
        "email": email,
        "wallet_address": wallet_address
    }

@router.get("/search")
def search_users(query: str, exact: bool = False, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    """
    Search for users by username or email
    - query: search term
    - exact: if True, only return exact matches
    """
    try:
        search_term = query.strip()
        
        if not search_term or len(search_term) < 2:
            return []
        
        # Create SQL query based on exact match parameter
        if exact:
            sql_query = """
                SELECT id, username, email, wallet_address
                FROM users
                WHERE username = :query OR email = :query
                LIMIT 10
            """
        else:
            # Use ILIKE for case-insensitive partial matching
            sql_query = """
                SELECT id, username, email, wallet_address
                FROM users
                WHERE username ILIKE :pattern OR email ILIKE :pattern
                LIMIT 10
            """
            search_term = f"%{search_term}%"
            
        # Execute the query
        results = db.execute(
            text(sql_query),
            {"query": query, "pattern": search_term} if not exact else {"query": query}
        ).fetchall()
        
        # Format the results
        users = []
        for user in results:
            users.append({
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "wallet_address": user[3]
            })
            
        return users
    except Exception as e:
        print(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching users: {str(e)}"
        )

# Add these new models at the end of the existing models section
class UserUpdateProfile(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    date_of_birth: Optional[str] = None
    phone_number: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

class NotificationSettings(BaseModel):
    email_notifications: Optional[bool] = True
    push_notifications: Optional[bool] = True
    transaction_alerts: Optional[bool] = True
    marketing_emails: Optional[bool] = False
    login_alerts: Optional[bool] = True
    security_alerts: Optional[bool] = True

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

@router.put("/update-profile/{user_id}")
def update_user_profile(
    user_id: int, 
    profile: UserUpdateProfile, 
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    """Update user profile information"""
    # Check if the user exists
    user = db.execute(
        text("SELECT id, username FROM users WHERE id = :user_id"), 
        {"user_id": user_id}
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check permissions: only the user themselves can update their profile (or an admin)
    current_user_data = db.execute(
        text("SELECT id, role FROM users WHERE username = :username"),
        {"username": current_user}
    ).first()
    
    if not current_user_data:
        raise HTTPException(status_code=404, detail="Current user not found")
    
    current_user_id, role = current_user_data
    if current_user_id != user_id and role != "admin":
        raise HTTPException(status_code=403, detail="You don't have permission to update this user's profile")
    
    try:
        # Update email address in users table if provided
        if profile.email:
            # Check if email is already in use by a different user
            existing_email = db.execute(
                text("SELECT id FROM users WHERE email = :email AND id != :user_id"),
                {"email": profile.email, "user_id": user_id}
            ).first()
            
            if existing_email:
                raise HTTPException(status_code=400, detail="Email address is already in use")
            
            db.execute(
                text("UPDATE users SET email = :email WHERE id = :user_id"),
                {"email": profile.email, "user_id": user_id}
            )
        
        # Check if metadata already exists
        existing = db.execute(
            text("SELECT id FROM user_metadata WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).first()
        
        # Get existing profile data or create new if it doesn't exist
        if existing:
            current_profile_data = db.execute(
                text("SELECT profile_data FROM user_metadata WHERE user_id = :user_id"),
                {"user_id": user_id}
            ).first()
            profile_data = current_profile_data[0] if current_profile_data and current_profile_data[0] else {}
        else:
            profile_data = {}
        
        # Merge new profile values
        profile_dict = {k: v for k, v in profile.dict().items() if v is not None}
        if profile_dict:
            if not profile_data:
                profile_data = profile_dict
            else:
                profile_data.update(profile_dict)
        
        # Process database update
        if existing:
            # Update existing record
            db.execute(
                text("""
                    UPDATE user_metadata SET 
                    first_name = :first_name,
                    last_name = :last_name,
                    date_of_birth = :date_of_birth,
                    country = :country,
                    country_code = :country_code,
                    profile_data = :profile_data,
                    updated_at = :updated_at
                    WHERE user_id = :user_id
                """),
                {
                    "user_id": user_id,
                    "first_name": profile.first_name,
                    "last_name": profile.last_name,
                    "date_of_birth": profile.date_of_birth,
                    "country": profile.country,
                    "country_code": profile.country_code,
                    "profile_data": profile_data,
                    "updated_at": datetime.utcnow()
                }
            )
        else:
            # Create new record
            db.execute(
                text("""
                    INSERT INTO user_metadata 
                    (user_id, first_name, last_name, date_of_birth, country, country_code, profile_data, created_at) 
                    VALUES 
                    (:user_id, :first_name, :last_name, :date_of_birth, :country, :country_code, :profile_data, :created_at)
                """),
                {
                    "user_id": user_id,
                    "first_name": profile.first_name,
                    "last_name": profile.last_name,
                    "date_of_birth": profile.date_of_birth,
                    "country": profile.country,
                    "country_code": profile.country_code,
                    "profile_data": profile_data,
                    "created_at": datetime.utcnow()
                }
            )
        
        db.commit()
        return {"message": "Profile updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")

@router.put("/notification-settings/{user_id}")
def update_notification_settings(
    user_id: int, 
    settings: NotificationSettings, 
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    """Update user notification settings"""
    # Check if the user exists
    user = db.execute(
        text("SELECT id, username FROM users WHERE id = :user_id"), 
        {"user_id": user_id}
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check permissions: only the user themselves can update their settings (or an admin)
    current_user_data = db.execute(
        text("SELECT id, role FROM users WHERE username = :username"),
        {"username": current_user}
    ).first()
    
    if not current_user_data:
        raise HTTPException(status_code=404, detail="Current user not found")
    
    current_user_id, role = current_user_data
    if current_user_id != user_id and role != "admin":
        raise HTTPException(status_code=403, detail="You don't have permission to update this user's notification settings")
    
    try:
        # Get existing metadata
        metadata = db.execute(
            text("SELECT id, profile_data FROM user_metadata WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).first()
        
        if metadata:
            metadata_id, profile_data = metadata
            
            # Extract notification settings
            if profile_data is None:
                profile_data = {}
            
            # Update notification settings
            if 'notification_settings' not in profile_data:
                profile_data['notification_settings'] = {}
                
            profile_data['notification_settings'] = settings.dict()
            
            # Update metadata
            db.execute(
                text("""
                    UPDATE user_metadata SET
                    profile_data = :profile_data,
                    updated_at = :updated_at
                    WHERE id = :id
                """),
                {
                    "id": metadata_id,
                    "profile_data": profile_data,
                    "updated_at": datetime.utcnow()
                }
            )
        else:
            # Create new metadata with notification settings
            profile_data = {
                'notification_settings': settings.dict()
            }
            
            db.execute(
                text("""
                    INSERT INTO user_metadata
                    (user_id, profile_data, created_at)
                    VALUES
                    (:user_id, :profile_data, :created_at)
                """),
                {
                    "user_id": user_id,
                    "profile_data": profile_data,
                    "created_at": datetime.utcnow()
                }
            )
        
        db.commit()
        return {"message": "Notification settings updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating notification settings: {str(e)}")

@router.put("/update-password/{user_id}")
def update_password(
    user_id: int, 
    password_update: PasswordUpdate, 
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    """Update user password"""
    # Check permissions: only the user themselves can update their password
    current_user_data = db.execute(
        text("SELECT id, username, hashed_password FROM users WHERE username = :username"),
        {"username": current_user}
    ).first()
    
    if not current_user_data:
        raise HTTPException(status_code=404, detail="Current user not found")
    
    current_user_id, username, hashed_password = current_user_data
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="You can only update your own password")
    
    # Verify current password
    if not bcrypt.checkpw(password_update.current_password.encode("utf-8"), hashed_password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    
    # Validate new password
    if len(password_update.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters long")
    
    try:
        # Hash new password
        new_hashed_password = bcrypt.hashpw(password_update.new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        # Update password
        db.execute(
            text("UPDATE users SET hashed_password = :hashed_password WHERE id = :user_id"),
            {"hashed_password": new_hashed_password, "user_id": user_id}
        )
        
        db.commit()
        return {"message": "Password updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating password: {str(e)}")

@router.get("/notification-settings/{user_id}")
def get_notification_settings(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    """Get user notification settings"""
    # Check permissions
    current_user_data = db.execute(
        text("SELECT id, role FROM users WHERE username = :username"),
        {"username": current_user}
    ).first()
    
    if not current_user_data:
        raise HTTPException(status_code=404, detail="Current user not found")
    
    current_user_id, role = current_user_data
    if current_user_id != user_id and role != "admin":
        raise HTTPException(status_code=403, detail="You don't have permission to view this user's notification settings")
    
    # Get metadata
    metadata = db.execute(
        text("SELECT profile_data FROM user_metadata WHERE user_id = :user_id"),
        {"user_id": user_id}
    ).first()
    
    # Default notification settings
    default_settings = {
        "email_notifications": True,
        "push_notifications": True,
        "transaction_alerts": True,
        "marketing_emails": False,
        "login_alerts": True,
        "security_alerts": True
    }
    
    if metadata and metadata[0] and 'notification_settings' in metadata[0]:
        settings = metadata[0]['notification_settings']
        
        # Ensure all expected keys are present
        for key in default_settings:
            if key not in settings:
                settings[key] = default_settings[key]
                
        return settings
    
    return default_settings

# Add avatar upload endpoint
class AvatarResponse(BaseModel):
    avatar_url: str

@router.post("/upload-avatar/{user_id}", response_model=AvatarResponse)
async def upload_avatar(
    user_id: int, 
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Upload a profile avatar image"""
    # Check permissions
    current_user_data = db.execute(
        text("SELECT id, role FROM users WHERE username = :username"),
        {"username": current_user}
    ).first()
    
    if not current_user_data:
        raise HTTPException(status_code=404, detail="Current user not found")
    
    current_user_id, role = current_user_data
    if current_user_id != user_id and role != "admin":
        raise HTTPException(status_code=403, detail="You don't have permission to update this user's avatar")
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif"]
    content_type = file.content_type
    
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail="Only JPEG, PNG, and GIF images are allowed"
        )
    
    # Create avatars directory if it doesn't exist
    upload_dir = "static/avatars"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # Generate unique filename to prevent overwriting
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{user_id}_{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save the file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving file: {str(e)}"
        )
    finally:
        file.file.close()
    
    # Generate URL for the avatar
    avatar_url = f"/static/avatars/{unique_filename}"
    
    # Update user metadata with the new avatar URL
    try:
        # Check if metadata already exists
        existing = db.execute(
            text("SELECT id FROM user_metadata WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).first()
        
        # Get existing profile data
        if existing:
            profile_data_result = db.execute(
                text("SELECT profile_data FROM user_metadata WHERE user_id = :user_id"),
                {"user_id": user_id}
            ).first()
            
            profile_data = profile_data_result[0] if profile_data_result and profile_data_result[0] else {}
        else:
            profile_data = {}
        
        # Update avatar URL in profile_data
        if not profile_data:
            profile_data = {"avatar_url": avatar_url}
        else:
            profile_data["avatar_url"] = avatar_url
        
        # Update or insert metadata record
        if existing:
            db.execute(
                text("""
                    UPDATE user_metadata SET
                    profile_data = :profile_data,
                    updated_at = :updated_at
                    WHERE user_id = :user_id
                """),
                {
                    "user_id": user_id,
                    "profile_data": profile_data,
                    "updated_at": datetime.utcnow()
                }
            )
        else:
            db.execute(
                text("""
                    INSERT INTO user_metadata
                    (user_id, profile_data, created_at)
                    VALUES
                    (:user_id, :profile_data, :created_at)
                """),
                {
                    "user_id": user_id,
                    "profile_data": profile_data,
                    "created_at": datetime.utcnow()
                }
            )
        
        db.commit()
        return {"avatar_url": avatar_url}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating user metadata: {str(e)}")
