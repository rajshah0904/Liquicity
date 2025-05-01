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
from app.services.email_service import (
    generate_verification_token, 
    get_token_expiry, 
    send_verification_email,
    send_password_reset_email
)
from passlib.context import CryptContext
from dotenv import load_dotenv
import secrets
import psycopg2
import logging

load_dotenv()

router = APIRouter()

# Get configuration
config = AppConfig()
SECRET_KEY = config.auth.secret_key
ALGORITHM = config.auth.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = config.auth.access_token_expire_minutes

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    country: Optional[str] = None
    nationality: Optional[str] = None

class UserRead(BaseModel):
    id: Optional[int] = None
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    country: Optional[str] = None
    nationality: Optional[str] = None
    message: Optional[str] = None

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str

class KycSubmitRequest(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: str
    country: str
    country_code: Optional[str] = None
    nationality: Optional[str] = None
    id_number: Optional[str] = None
    id_type: Optional[str] = None
    document_type: Optional[str] = None
    document_number: Optional[str] = None

@router.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if user with email already exists
        existing_user = db.execute(
            text("SELECT id, google_id FROM users WHERE email = :email"),
            {"email": user.email}
        ).first()
        
        if existing_user:
            # If user has a Google ID, redirect to Google sign in
            if existing_user[1]:  # google_id is not None
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This email is already registered with Google. Please sign in with Google instead."
                )
            else:
                # User exists but not with Google
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An account with this email already exists. Please sign in with your password."
                )
        
        # Hash the password
        hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        # Insert the user
        result = db.execute(
            text("""
                INSERT INTO users (
                    email, hashed_password, first_name, last_name, date_of_birth, country, nationality,
                    role, is_active, email_verified
                ) 
                VALUES (
                    :email, :hashed_password, :first_name, :last_name, :date_of_birth, :country, :nationality,
                    :role, :is_active, false
                )
                RETURNING id
            """),
            {
                "email": user.email,
                "hashed_password": hashed_password,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "date_of_birth": user.date_of_birth,
                "country": user.country,
                "nationality": user.nationality,
                "role": "user",
                "is_active": True
            }
        )
        db.commit()
        
        # Get the user ID from the result
        user_id = result.first()[0]
        
        # Create a wallet for the user with 0 balance
        db.execute(
            text("""
                INSERT INTO wallets (user_id, fiat_balance, base_currency) 
                VALUES (:user_id, :fiat_balance, :base_currency)
            """),
            {
                "user_id": user_id,
                "fiat_balance": 0.0,
                "base_currency": "USD"
            }
        )
        db.commit()
        
        # Generate and send email verification
        try:
            send_verification_email(user.email, generate_verification_token())
        except Exception as e:
            logging.error(f"Failed to send verification email: {str(e)}")
            # Continue with user creation even if email sending fails
        
        return {
            "id": user_id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_of_birth": user.date_of_birth,
            "country": user.country,
            "nationality": user.nationality,
            "message": "User registered successfully. Please check your email for verification."
        }
    
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        db.rollback()
        logging.error(f"User creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

@router.post("/request-password-reset/")
async def request_password_reset(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request a password reset email."""
    try:
        # Check if user exists
        user = db.execute(
            text("SELECT id, email FROM users WHERE email = :email"),
            {"email": request.email}
        ).first()
        
        if not user:
            # Don't reveal if email exists or not
            return {"message": "If your email is registered, you will receive a password reset link."}
        
        user_id, email = user
        
        # Generate reset token
        token = generate_verification_token()
        expires_at = get_token_expiry()
        
        # Update user with reset token
        db.execute(
            text("""
                UPDATE users 
                SET reset_password_token = :token,
                    reset_password_token_expires_at = :expires_at
                WHERE id = :user_id
            """),
            {
                "token": token,
                "expires_at": expires_at,
                "user_id": user_id
            }
        )
        db.commit()
        
        # Send password reset email
        sent = send_password_reset_email(email, token)
        
        if not sent:
            raise HTTPException(
                status_code=500,
                detail="Failed to send password reset email. Please try again later."
            )
        
        return {"message": "If your email is registered, you will receive a password reset link."}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset-password/")
async def reset_password(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password using the token from email."""
    try:
        # Find user with valid reset token
        user = db.execute(
            text("""
                SELECT id, reset_password_token_expires_at 
                FROM users 
                WHERE reset_password_token = :token
            """),
            {"token": request.token}
        ).first()
        
        if not user:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        user_id, expires_at = user
        
        # Check if token has expired
        if expires_at and expires_at < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Reset token has expired")
        
        # Hash new password
        hashed_password = bcrypt.hashpw(request.new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        # Update password and clear reset token
        db.execute(
            text("""
                UPDATE users 
                SET hashed_password = :hashed_password,
                    reset_password_token = NULL,
                    reset_password_token_expires_at = NULL
                WHERE id = :user_id
            """),
            {
                "hashed_password": hashed_password,
                "user_id": user_id
            }
        )
        db.commit()
        
        return {"message": "Password has been reset successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def read_users(db: Session = Depends(get_db)):
    users = db.execute(text("SELECT id, email, wallet_address FROM users")).fetchall()
    return [{"id": user[0], "email": user[1], "wallet_address": user[2]} for user in users]

class LoginRequest(BaseModel):
    email: EmailStr

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
    This endpoint verifies email and password credentials and returns an access token.
    """
    try:
        # Get user by email
        query = "SELECT id, hashed_password, role, email_verified, email, google_id FROM users WHERE email = :email"
        params = {"email": user.email}
        
        result = db.execute(text(query), params).first()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id, hashed_password, role, email_verified, email, google_id = result
        
        # If user has a Google account without a password, they should use Google login
        if google_id and not hashed_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This account uses Google login. Please use Google login instead.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not hashed_password or not bcrypt.checkpw(user.password.encode("utf-8"), hashed_password.encode("utf-8")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # We allow login even if email is not verified, but we'll include a flag in the response
        email_is_verified = email_verified
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={'sub': email, 'user_id': user_id, 'role': role}, 
            expires_delta=access_token_expires
        )
        
        print(f"User {email} (ID: {user_id}) logged in successfully")
        
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "email_verified": email_is_verified
        }
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Internal server error during login: {str(e)}"
        )
    
@router.get("/user/")
def get_user_details(email: str = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get user using raw SQL to avoid ORM schema issues
    result = db.execute(
        text("SELECT id, email, first_name, last_name, date_of_birth, country, nationality, wallet_address FROM users WHERE email = :email"),
        {"email": email}
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id, email, first_name, last_name, date_of_birth, country, nationality, wallet_address = result
    
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
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "date_of_birth": date_of_birth,
        "country": country,
        "nationality": nationality,
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
    user = db.execute(text("SELECT id FROM users WHERE id = :user_id"), {"user_id": user_id}).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check permissions: only admins or the user themselves can update their metadata
    current_user_data = db.execute(
        text("SELECT id, role FROM users WHERE email = :email"),
        {"email": current_user}
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
        text("SELECT id, role FROM users WHERE email = :email"),
        {"email": current_user}
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
    Check if a user has completed identity verification
    """
    # Check permissions: only admins or the user themselves can check verification status
    current_user_data = db.execute(
        text("SELECT id, role FROM users WHERE email = :email"),
        {"email": current_user}
    ).first()
    if not current_user_data:
        raise HTTPException(status_code=404, detail="Current user not found")
    current_user_id, role = current_user_data
    if current_user_id != user_id and role != "admin":
        raise HTTPException(status_code=403, detail="You don't have permission to check this user's verification status")
    
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
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

@router.post("/register-test/")
def create_test_user(user: TestUserCreate, db: Session = Depends(get_db)):
    """Create a test user account - development purposes only"""
    try:
        # Check if user with email already exists
        result = db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": user.email}).first()
        if result:
            raise HTTPException(status_code=400, detail="Email already registered")
        # Hash the password
        hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        # Insert the new user
        result = db.execute(
            text("""
                INSERT INTO users (
                    email, hashed_password, first_name, last_name, role, is_active, 
                    email_verified
                )
                VALUES (
                    :email, :hashed_password, :first_name, :last_name, :role, :is_active,
                    :email_verified
                )
                RETURNING id
            """),
            {
                "email": user.email,
                "hashed_password": hashed_password,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": "user",
                "is_active": True,
                "email_verified": True
            }
        )
        
        db.commit()
        user_id = result.first()[0]
        
        # Create a wallet for the new user
        db.execute(
            text("""
                INSERT INTO wallets (user_id, fiat_balance, base_currency) 
                VALUES (:user_id, :fiat_balance, :base_currency)
            """),
            {
                "user_id": user_id,
                "fiat_balance": 1000.0,  # Start with test funds
                "base_currency": "USD"
            }
        )
        db.commit()
        
        return {"id": user_id, "email": user.email, "message": "Test user created successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating test user: {str(e)}")

@router.get("/profile/{user_id}")
def get_user_profile(user_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    """Get a user's profile data"""
    try:
        # Get the basic user info
        user = db.execute(
            text("SELECT id, email, wallet_address FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        ).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user's metadata
        metadata = db.execute(
            text("""
                SELECT first_name, last_name, date_of_birth, country, profile_data
                FROM user_metadata
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        ).first()
        
        result = {
            "id": user[0],
            "email": user[1],
            "wallet_address": user[2],
        }
        
        if metadata:
            result.update({
                "first_name": metadata[0],
                "last_name": metadata[1],
                "date_of_birth": metadata[2],
                "country": metadata[3],
                "profile_data": metadata[4] or {}
            })
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user profile: {str(e)}")

@router.get("/search")
def search_users(query: str, exact: bool = False, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    """Search for users by email or name"""
    try:
        # Check permissions, only admins can use this endpoint
        role_result = db.execute(
            text("SELECT role FROM users WHERE email = :email"),
            {"email": current_user}
        ).first()
        
        if not role_result or role_result[0] != "admin":
            raise HTTPException(status_code=403, detail="Only administrators can search for users")
        
        # Prepare the search query
        if exact:
            search_term = f"{query}"
            sql_query = "SELECT id, email, wallet_address FROM users WHERE email = :search_term"
        else:
            search_term = f"%{query}%"
            sql_query = """
                SELECT id, email, wallet_address 
                FROM users
                WHERE email ILIKE :search_term
            """
            
        # Execute the search
        results = db.execute(text(sql_query), {"search_term": search_term}).fetchall()
        
        # Format the results
        users = []
        for row in results:
            user_id, email, wallet_address = row
            users.append({
                "id": user_id,
                "email": email,
                "wallet_address": wallet_address
            })
            
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

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
    try:
        # Check if user exists
        user = db.execute(text("SELECT id FROM users WHERE id = :user_id"), {"user_id": user_id}).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check permissions: only the user themselves or an admin can update profile
        current_user_data = db.execute(
            text("SELECT id, role FROM users WHERE email = :email"),
            {"email": current_user}
        ).first()
        
        if not current_user_data:
            raise HTTPException(status_code=404, detail="Current user not found")
        
        current_user_id, role = current_user_data
        
        # Only allow users to update their own profile or admins to update any user's profile
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
    """Update user notification preferences"""
    try:
        # Check if user exists
        user = db.execute(text("SELECT id FROM users WHERE id = :user_id"), {"user_id": user_id}).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check permissions: only the user themselves or an admin can update notification settings
        current_user_data = db.execute(
            text("SELECT id, role FROM users WHERE email = :email"),
            {"email": current_user}
        ).first()
        
        if not current_user_data:
            raise HTTPException(status_code=404, detail="Current user not found")
        
        current_user_id, role = current_user_data
        
        # Only allow users to update their own settings or admins to update any user's settings
        if current_user_id != user_id and role != "admin":
            raise HTTPException(status_code=403, detail="You don't have permission to update this user's notification settings")
        
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
    """Update a user's password"""
    try:
        # Verify the current user is updating their own password or is an admin
        current_user_data = db.execute(
            text("SELECT id, role, hashed_password FROM users WHERE email = :email"),
            {"email": current_user}
        ).first()
        
        if not current_user_data:
            raise HTTPException(status_code=404, detail="Current user not found")
        
        current_user_id, role, hashed_password = current_user_data
        
        # Only allow users to update their own password, or admins to update any user
        if current_user_id != user_id and role != "admin":
            raise HTTPException(status_code=403, detail="You don't have permission to update this user's password")
        
        # Verify current password
        if not bcrypt.checkpw(password_update.current_password.encode("utf-8"), hashed_password.encode("utf-8")):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Hash new password
        new_hashed_password = bcrypt.hashpw(password_update.new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        # Update in database
        db.execute(
            text("UPDATE users SET hashed_password = :hashed_password WHERE id = :user_id"),
            {"hashed_password": new_hashed_password, "user_id": user_id}
        )
        db.commit()
        
        return {"message": "Password updated successfully"}
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating password: {str(e)}")

@router.get("/notification-settings/{user_id}")
def get_notification_settings(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    """Get a user's notification settings"""
    try:
        # Check permissions: only the user themselves or admins can view notification settings
        current_user_data = db.execute(
            text("SELECT id, role FROM users WHERE email = :email"),
            {"email": current_user}
        ).first()
        
        if not current_user_data:
            raise HTTPException(status_code=404, detail="Current user not found")
        
        current_user_id, role = current_user_data
        
        # Verify permissions - only allow users to view their own settings or admins to view any
        if current_user_id != user_id and role != "admin":
            raise HTTPException(status_code=403, detail="You don't have permission to view these notification settings")
        
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting notification settings: {str(e)}")

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
    """Upload a user avatar image"""
    try:
        # Check permissions: only the user themselves or an admin can upload their avatar
        current_user_data = db.execute(
            text("SELECT id, role FROM users WHERE email = :email"),
            {"email": current_user}
        ).first()
        
        if not current_user_data:
            raise HTTPException(status_code=404, detail="Current user not found")
        
        current_user_id, role = current_user_data
        
        # Only allow users to upload their own avatar or admins to upload any user's avatar
        if current_user_id != user_id and role != "admin":
            raise HTTPException(status_code=403, detail="You don't have permission to upload this user's avatar")
        
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading avatar: {str(e)}")

class VerificationEmailRequest(BaseModel):
    email: str
    user_id: Optional[int] = None
    password: Optional[str] = None  # Password for new users

class VerifyEmailRequest(BaseModel):
    token: str

@router.post("/send-verification-email/")
async def send_email_verification(request: VerificationEmailRequest, db: Session = Depends(get_db)):
    """
    Send a verification email to the user's email address.
    
    This endpoint:
    1. Validates the email exists in the database
    2. Generates a verification token
    3. Updates the user record with the token and expiration
    4. Sends the verification email
    5. For new users, records the verification in pending_verifications
    """
    try:
        print(f"Received verification email request for email: {request.email}")
        print(f"Looking up user by email: {request.email}")
        
        # Check if user already exists
        user = db.execute(
            text("SELECT id, email_verified FROM users WHERE email = :email"),
            {"email": request.email}
        ).first()
        
        # Generate verification token
        token = generate_verification_token()
        expires_at = get_token_expiry()
        
        if not user:
            # This is a new registration
            print(f"User with email {request.email} not found, creating a temporary record")
            
            # For new users with no account, we need a password
            if not request.password:
                raise HTTPException(
                    status_code=400, 
                    detail="Password is required for new users. Please provide a password to create your account."
                )
            
            # Hash the password
            hashed_password = bcrypt.hashpw(request.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            
            # Make sure pending_verifications table exists
            db.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS pending_verifications (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) NOT NULL,
                        token VARCHAR(255) NOT NULL,
                        expires_at TIMESTAMP NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                        verified BOOLEAN NOT NULL DEFAULT FALSE,
                        verified_at TIMESTAMP,
                        hashed_password VARCHAR(255),
                        username VARCHAR(255)
                    )
                """)
            )
            db.commit()
            
            # Check if pending verification already exists
            existing = db.execute(
                text("SELECT id FROM pending_verifications WHERE email = :email AND verified = false"),
                {"email": request.email}
            ).first()
            
            if existing:
                # Update existing record
                db.execute(
                    text("""
                        UPDATE pending_verifications
                        SET token = :token,
                            expires_at = :expires_at,
                            created_at = NOW(),
                            hashed_password = :hashed_password
                        WHERE email = :email AND verified = false
                    """),
                    {
                        "token": token,
                        "expires_at": expires_at,
                        "email": request.email,
                        "hashed_password": hashed_password
                    }
                )
            else:
                # Insert new record
                db.execute(
                    text("""
                        INSERT INTO pending_verifications
                        (email, token, expires_at, hashed_password)
                        VALUES
                        (:email, :token, :expires_at, :hashed_password)
                    """),
                    {
                        "email": request.email,
                        "token": token,
                        "expires_at": expires_at,
                        "hashed_password": hashed_password
                    }
                )
            db.commit()
        else:
            # Existing user, update verification token
            user_id, email_verified = user
            print(f"User found/created with ID: {user_id}, Email: {request.email}, Verified: {email_verified}")
            
            # If already verified, just return success
            if email_verified:
                return {"message": "Email already verified", "email": request.email}
            
            # Update verification token
            db.execute(
                text("""
                    UPDATE users 
                    SET verification_token = :token,
                        verification_token_expires_at = :expires_at
                    WHERE id = :user_id
                """),
                {
                    "token": token,
                    "expires_at": expires_at,
                    "user_id": user_id
                }
            )
            db.commit()
            print(f"Generated verification token: {token[:10]}..., expires at {expires_at}")
            print(f"Updated user record with verification token")
            
            # Send verification email
            print(f"Sending verification email to {request.email}")
            sent = send_verification_email(request.email, token)
        
        if sent:
            return {"message": "Verification email sent successfully", "email": request.email}
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to send verification email. Please try again later."
            )
    
    except Exception as e:
        db.rollback()
        print(f"Error sending verification email: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to send verification email: {str(e)}")

@router.post("/verify-email/")
async def verify_email(request: VerifyEmailRequest, db: Session = Depends(get_db)):
    """
    Verify a user's email using the verification token.
    
    This endpoint:
    1. Finds the user with the given token
    2. Validates the token hasn't expired
    3. Marks the user's email as verified
    4. Creates a new user if none exists with this token
    """
    try:
        print(f"DEBUG: Starting verify_email with token: {request.token[:10]}...")
        
        # Extract email and hashed_password from pending_verifications if exists
        print(f"DEBUG: Checking pending_verifications table for token")
        sql_query = """
            SELECT email, hashed_password FROM pending_verifications 
            WHERE token = :token AND verified = false
        """
        print(f"DEBUG: SQL Query 1: {sql_query}")
        pending = db.execute(
            text(sql_query),
            {"token": request.token}
        ).first()
        print(f"DEBUG: Pending verification result: {pending}")
        
        # Find the user with the given token
        print(f"DEBUG: Checking users table for token")
        sql_query2 = """
            SELECT id, email, verification_token_expires_at, role 
                FROM users 
                WHERE verification_token = :token
        """
        print(f"DEBUG: SQL Query 2: {sql_query2}")
        user = db.execute(
            text(sql_query2),
            {"token": request.token}
        ).first()
        print(f"DEBUG: User query result: {user}")
        
        # Handle case when token matches a pending verification but no user exists
        new_user_creation = False
        if not user and pending:
            print(f"DEBUG: Token matches pending verification but user doesn't exist")
            email = pending[0]
            hashed_password = pending[1]
            new_user_creation = True
            
            # Generate a temporary password if none was provided
            if not hashed_password:
                temp_password = secrets.token_urlsafe(16)
                hashed_password = bcrypt.hashpw(temp_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            
            # Create new user
            print(f"DEBUG: Creating new user with email: {email}")
            result = db.execute(
                text("""
                    INSERT INTO users (
                        email, hashed_password, role, is_active, email_verified,
                        created_at
                    ) 
                    VALUES (
                        :email, :hashed_password, 'user', true, true,
                        NOW()
                    )
                    RETURNING id
                """),
                {
                    "email": email,
                    "hashed_password": hashed_password
                }
            )
            db.commit()
            
            # Get the newly created user ID
            user_id = result.first()[0]
            print(f"DEBUG: Created new user with ID: {user_id}")
            
            # Create a wallet for the new user
            print(f"DEBUG: Creating wallet for user ID: {user_id}")
            db.execute(
                text("""
                    INSERT INTO wallets (user_id, fiat_balance, base_currency) 
                    VALUES (:user_id, :fiat_balance, :base_currency)
                """),
                {
                    "user_id": user_id,
                    "fiat_balance": 0.0,
                    "base_currency": "USD"
                }
            )
            db.commit()
            
            # Mark pending verification as verified
            print(f"DEBUG: Marking pending verification as verified")
            db.execute(
                text("""
                    UPDATE pending_verifications
                    SET verified = true,
                        verified_at = NOW()
                    WHERE token = :token
                """),
                {"token": request.token}
            )
            db.commit()
            
            # Create access token for automatic login
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={'sub': email, 'user_id': user_id, 'role': 'user'},
                expires_delta=access_token_expires
            )
            print(f"DEBUG: Successfully created access token for new user")
            
            return {
                "message": "Email verified and account created successfully",
                "email": email,
                "access_token": access_token,
                "token_type": "bearer",
                "requires_kyc": True,
                "user_id": user_id
            }
        
        if not user:
            print(f"DEBUG: Token not found in users or pending_verifications")
            raise HTTPException(
                status_code=400,
                detail="Invalid verification token"
            )
        
        print(f"DEBUG: User found with token: {user}")
        user_id, email, expires_at, role = user
        
        # Check if token has expired
        if expires_at and expires_at < datetime.utcnow():
            # Generate new token if expired
            token = generate_verification_token()
            new_expires_at = get_token_expiry()
            
            # Update user with new token
            db.execute(
                text("""
                    UPDATE users 
                    SET verification_token = :token,
                        verification_token_expires_at = :expires_at
                    WHERE id = :user_id
                """),
                {
                    "token": token,
                    "expires_at": new_expires_at,
                    "user_id": user_id
                }
            )
            db.commit()
            
            # Send new verification email
            send_verification_email(email, token)
            
            raise HTTPException(
                status_code=400,
                detail="Verification token has expired. A new token has been sent to your email."
            )
        
        # Mark the user's email as verified
        db.execute(
            text("""
                UPDATE users 
                SET email_verified = true,
                    verification_token = NULL,
                    verification_token_expires_at = NULL
                WHERE id = :user_id
            """),
            {"user_id": user_id}
        )
        db.commit()
        
        # Create access token for automatic login
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={'sub': email, 'user_id': user_id, 'role': role or 'user'}, 
            expires_delta=access_token_expires
        )
        
        return {
            "message": "Email verified successfully",
            "email": email,
            "access_token": access_token,
            "token_type": "bearer",
            "requires_kyc": False,
            "user_id": user_id
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error verifying email: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

class GoogleAuthRequest(BaseModel):
    email: EmailStr
    google_id: str
    name: Optional[str] = None

@router.post("/google-auth/")
async def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    try:
        # Check if user exists by email
        existing_user = db.execute(
            text("SELECT id, google_id, hashed_password, email_verified FROM users WHERE email = :email"),
            {"email": request.email}
        ).first()
        
        if existing_user:
            user_id, google_id, hashed_password, email_verified = existing_user
            
            # If user exists but has a password and no Google ID, they registered normally
            if hashed_password and not google_id:
                return {
                    "success": False,
                    "message": "This email is already registered with a password. Please use regular login instead.",
                    "redirect": "/login"
                }
            
            # Update Google ID if it's not set
            if not google_id:
                db.execute(
                    text("UPDATE users SET google_id = :google_id WHERE id = :id"),
                    {"google_id": request.google_id, "id": user_id}
                )
                db.commit()
            
            # Verify email if not already verified
            if not email_verified:
                db.execute(
                    text("UPDATE users SET email_verified = TRUE WHERE id = :id"),
                    {"id": user_id}
                )
                db.commit()
            
            # Generate access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": str(user_id)}, expires_delta=access_token_expires
            )
            
            return {"access_token": access_token, "token_type": "bearer", "user_id": user_id}
        
        # User doesn't exist, create a new user
        # Split the name into first name and last name
        name_parts = request.name.split() if request.name else ["", ""]
        first_name = name_parts[0] if name_parts else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        # Insert user
        db.execute(
            text("""
                INSERT INTO users (
                    email, google_id, first_name, last_name,
                    role, is_active, email_verified
                ) 
                VALUES (
                    :email, :google_id, :first_name, :last_name,
                    :role, :is_active, :email_verified
                )
            """),
            {
                "email": request.email,
                "google_id": request.google_id,
                "first_name": first_name,
                "last_name": last_name,
                "role": "user",
                "is_active": True,
                "email_verified": True
            }
        )
        db.commit()
        
        # Get the newly created user ID
        new_user = db.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": request.email}
        ).first()
        user_id = new_user[0]
        
        # Create a wallet for the new user
        db.execute(
            text("""
                INSERT INTO wallets (user_id, fiat_balance, base_currency) 
                VALUES (:user_id, :fiat_balance, :base_currency)
            """),
            {
                "user_id": user_id,
                "fiat_balance": 0.0,
                "base_currency": "USD"
            }
        )
        db.commit()
        
        # Generate access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user_id)}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer", "user_id": user_id}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Google authentication error: {str(e)}")

@router.post("/send-login-link/")
async def send_login_link(request: VerificationEmailRequest, db: Session = Depends(get_db)):
    """
    Send a login link to the user's email address.
    
    This endpoint:
    1. Validates the email exists in the database
    2. Generates a login token
    3. Updates the user record with the token and expiration
    4. Sends the login verification email
    """
    try:
        print(f"Received login link request for email: {request.email}")
        
        # Verify the email exists in the database
        user = db.execute(
            text("SELECT id, email, email_verified FROM users WHERE email = :email"),
            {"email": request.email}
        ).first()
        
        if not user:
            print(f"User with email {request.email} not found")
            # For security reasons, don't reveal that the email doesn't exist
            return {"message": "If your email is registered, you will receive a login link", "email": request.email}
        
        user_id, email, email_verified = user
        
        # Generate login token
        token = generate_verification_token()
        expires_at = get_token_expiry()
        print(f"Generated login token: {token[:10]}..., expires at {expires_at}")
        
        # Update the user record with the login token (use verification_token for simplicity)
        db.execute(
            text("""
                UPDATE users 
                SET verification_token = :token,
                    verification_token_expires_at = :expires_at
                WHERE id = :user_id
            """),
            {
                "token": token,
                "expires_at": expires_at,
                "user_id": user_id
            }
        )
        db.commit()
        print(f"Updated user record with login token")
        
        # Send the login verification email
        print(f"Sending login email to {email}")
        sent = send_verification_email(email, token)
        
        if sent:
            print(f"Login email sent successfully to {email}")
            return {"message": "Login link sent successfully", "email": email}
        else:
            print(f"Failed to send login email to {email}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to send login email. Please try again later."
            )
    
    except Exception as e:
        db.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"Error sending login email: {str(e)}")
        print(f"Traceback: {error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

@router.post("/verify-login-link/")
async def verify_login_link(request: VerifyEmailRequest, db: Session = Depends(get_db)):
    """
    Verify a user's login link token and generate an access token.
    
    This endpoint:
    1. Finds the user with the given token
    2. Validates the token hasn't expired
    3. Returns an access token for automatic login
    """
    try:
        print(f"DEBUG: Starting verify_login_link with token: {request.token[:10]}...")
        
        # Find the user with the given token
        print(f"DEBUG: Checking users table for token")
        sql_query = """
            SELECT id, email, verification_token_expires_at, role 
            FROM users 
            WHERE verification_token = :token
        """
        print(f"DEBUG: SQL Query: {sql_query}")
        user = db.execute(
            text(sql_query),
            {"token": request.token}
        ).first()
        print(f"DEBUG: User query result: {user}")
        
        if not user:
            print(f"DEBUG: Token not found in users table")
            raise HTTPException(
                status_code=400,
                detail="Invalid login token"
            )
        
        print(f"DEBUG: User found with token: {user}")
        user_id, email, expires_at, role = user
        
        # Check if token has expired
        if expires_at and expires_at < datetime.utcnow():
            # Generate new token if expired
            token = generate_verification_token()
            new_expires_at = get_token_expiry()
            
            # Update user with new token
            db.execute(
                text("""
                    UPDATE users 
                    SET verification_token = :token,
                        verification_token_expires_at = :expires_at
                    WHERE id = :user_id
                """),
                {
                    "token": token,
                    "expires_at": new_expires_at,
                    "user_id": user_id
                }
            )
            db.commit()
            
            # Send new verification email
            send_verification_email(email, token)
            
            raise HTTPException(
                status_code=400,
                detail="Login token has expired. A new token has been sent to your email."
            )
            
        # Clear the verification token to prevent reuse
        db.execute(
            text("""
                UPDATE users 
                SET verification_token = NULL,
                    verification_token_expires_at = NULL
                WHERE id = :user_id
            """),
            {"user_id": user_id}
        )
        db.commit()
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={'sub': email, 'user_id': user_id, 'role': role or 'user'}, 
            expires_delta=access_token_expires
        )
        
        print(f"User {email} (ID: {user_id}) logged in successfully via email link")
        
        return {"access_token": access_token, "token_type": "bearer"}
            
    except Exception as e:
        db.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"Error verifying login token: {str(e)}")
        print(f"Traceback: {error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

def add_nullable_password_column():
    """Make the hashed_password column nullable for Google Auth users."""
    try:
        # Connect to the database
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("Error: DATABASE_URL environment variable not set")
            return False
            
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Alter the column to make it nullable
        cursor.execute("""
            ALTER TABLE users 
            ALTER COLUMN hashed_password DROP NOT NULL;
        """)
        
        conn.commit()
        print("Successfully made hashed_password column nullable")
        
        # Close the connection
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error making hashed_password nullable: {e}")
        return False

# Add this function to the startup event of your application
# in app/main.py before app.include_router() calls:
#
# @app.on_event("startup")
# async def startup_event():
#     add_nullable_password_column()

@router.post("/kyc/submit/")
async def submit_kyc(
    request: KycSubmitRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Submit KYC info and update user metadata"""
    try:
        # Get the current user's ID
        user_row = db.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": current_user}
        ).first()
        if not user_row:
            raise HTTPException(status_code=404, detail="User not found")
        user_id = user_row[0]

        # Update nationality in users table if provided
        if request.nationality is not None:
            db.execute(
                text("UPDATE users SET nationality = :nationality WHERE id = :user_id"),
                {"nationality": request.nationality, "user_id": user_id}
            )

        # Upsert into user_metadata
        existing = db.execute(
            text("SELECT id FROM user_metadata WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).first()
        if existing:
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
                        updated_at = :updated_at
                    WHERE user_id = :user_id
                """),
                {
                    "user_id": user_id,
                    "first_name": request.first_name,
                    "last_name": request.last_name,
                    "date_of_birth": request.date_of_birth,
                    "country": request.country,
                    "country_code": request.country_code,
                    "id_number": request.id_number,
                    "id_type": request.id_type,
                    "document_type": request.document_type,
                    "document_number": request.document_number,
                    "updated_at": datetime.utcnow()
                }
            )
        else:
            db.execute(
                text("""
                    INSERT INTO user_metadata (
                        user_id, first_name, last_name, date_of_birth, country, country_code,
                        id_number, id_type, document_type, document_number, created_at
                    ) VALUES (
                        :user_id, :first_name, :last_name, :date_of_birth, :country, :country_code,
                        :id_number, :id_type, :document_type, :document_number, :created_at
                    )
                """),
                {
                    "user_id": user_id,
                    "first_name": request.first_name,
                    "last_name": request.last_name,
                    "date_of_birth": request.date_of_birth,
                    "country": request.country,
                    "country_code": request.country_code,
                    "id_number": request.id_number,
                    "id_type": request.id_type,
                    "document_type": request.document_type,
                    "document_number": request.document_number,
                    "created_at": datetime.utcnow()
                }
            )
        db.commit()
        return {"message": "KYC information submitted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error submitting KYC info: {str(e)}")
