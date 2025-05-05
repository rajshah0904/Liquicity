from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from app.database import get_db
from app.models import User, Wallet
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import os
import shutil
import uuid
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from app.dependencies.auth import get_current_user  # Auth0 JWT validation
from datetime import datetime
import logging
import bcrypt

load_dotenv()

router = APIRouter()

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
    skip_verification: Optional[bool] = False

@router.get("/")
def read_users(db: Session = Depends(get_db)):
    users = db.execute(text("SELECT id, email, wallet_address FROM users")).fetchall()
    return [{"id": user[0], "email": user[1], "wallet_address": user[2]} for user in users]

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

@router.post("/register", tags=["auth"])
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

@router.post("/kyc/submit", tags=["kyc"])
async def submit_kyc(
    first_name: str = Form(...),
    last_name: str = Form(...),
    date_of_birth: str = Form(...),
    country: str = Form(...),
    country_code: Optional[str] = Form(None),
    nationality: Optional[str] = Form(None),
    id_number: Optional[str] = Form(None),
    id_type: Optional[str] = Form(None),
    document_type: Optional[str] = Form(None),
    document_number: Optional[str] = Form(None),
    skip_verification: Optional[bool] = Form(True),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Submit KYC info and update user metadata"""
    try:
        # Create or fetch user_id
        user_row = db.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": current_user}
        ).first()
        if user_row:
            user_id = user_row[0]
        else:
            result = db.execute(
                text("INSERT INTO users (email) VALUES (:email) RETURNING id"),
                {"email": current_user}
            )
            user_id = result.fetchone()[0]
            db.commit()

        # Update nationality
        if nationality:
            db.execute(
                text("UPDATE users SET nationality = :nationality WHERE id = :user_id"),
                {"nationality": nationality, "user_id": user_id}
            )

        # Upsert metadata
        existing = db.execute(
            text("SELECT id FROM user_metadata WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).first()
        if existing:
            db.execute(
                text(
                    """
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
                    "first_name": first_name,
                    "last_name": last_name,
                    "date_of_birth": date_of_birth,
                    "country": country,
                    "country_code": country_code,
                    "id_number": id_number,
                    "id_type": id_type,
                    "document_type": document_type,
                    "document_number": document_number,
                    "updated_at": datetime.utcnow()
                }
            )
        else:
            db.execute(
                text(
                    """
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
                    "first_name": first_name,
                    "last_name": last_name,
                    "date_of_birth": date_of_birth,
                    "country": country,
                    "country_code": country_code,
                    "id_number": id_number,
                    "id_type": id_type,
                    "document_type": document_type,
                    "document_number": document_number,
                    "created_at": datetime.utcnow()
                }
            )

        # Optionally auto-approve
        if skip_verification:
            # Mark user as verified
            db.execute(
                text(
                    """
                    UPDATE users
                    SET is_verified = TRUE
                    WHERE id = :user_id
                    """
                ),
                {"user_id": user_id}
            )
            # Update metadata verification status
            db.execute(
                text(
                    """
                    UPDATE user_metadata
                    SET verification_status = 'verified',
                        verified_at = :verified_at,
                        updated_at = :updated_at
                    WHERE user_id = :user_id
                    """
                ),
                {
                    "user_id": user_id,
                    "verified_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            )
            db.commit()

        db.commit()
        return {"message": "KYC submitted", "user_id": user_id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error submitting KYC info: {str(e)}")

# Add new models for Auth0 integration
class Auth0UserCheck(BaseModel):
    auth0_id: str
    email: EmailStr

class Auth0UserCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    auth0_id: str

@router.get("/check", tags=["auth"])
async def check_user_exists(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Check if user exists in our database and if KYC is complete"""
    auth0_id = current_user.get("sub")
    email = current_user.get("email")
    
    # Check user in database
    user = db.execute(
        text("SELECT id, email, first_name, last_name, country FROM users WHERE email = :email"),
        {"email": email}
    ).first()
    
    if user:
        # Check if KYC is complete by verifying required fields
        kyc_complete = all([
            user.first_name, 
            user.last_name, 
            user.country
        ])
        
        return {
            "exists": True,
            "kyc_complete": kyc_complete
        }
    
    return {"exists": False, "kyc_complete": False}

@router.get("/kyc/{user_id}/status", tags=["kyc"])
async def get_kyc_status(user_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    result = db.execute(
        text("SELECT status FROM kyc_verifications WHERE user_id = :user_id"),
        {"user_id": user_id}
    ).first()
    return {"status": result[0] if result else "pending"}
