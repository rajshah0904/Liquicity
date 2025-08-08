from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, constr
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional, List
from ..database import get_db
from ..auth import get_current_user
from ..models import User, BridgeCustomer
from ..utils.currency_utils import get_supported_regions

router = APIRouter(prefix="/user", tags=["user_profile"])

class RegionIn(BaseModel):
    region: constr(min_length=2, max_length=32)

@router.get("/regions")
async def get_supported_regions_endpoint():
    """Get list of supported regions for region selection."""
    return {
        "regions": get_supported_regions()
    }

@router.post("/region")
async def set_user_region(payload: RegionIn, db: Session = Depends(get_db), jwt=Depends(get_current_user)):
    """Set user's region which determines their fiat currency."""
    user = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate region
    supported_regions = [r[0] for r in get_supported_regions()]
    if payload.region.lower() not in supported_regions:
        raise HTTPException(status_code=400, detail="Unsupported region")
    
    # Update user's region
    user.region = payload.region.lower()
    db.commit()
    
    return {
        "region": user.region,
        "status": "updated"
    }

@router.get("")
async def get_profile(db: Session = Depends(get_db), jwt=Depends(get_current_user)):
    """Return the authenticated user's basic profile (id, email, region)."""
    user = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": str(user.id),
        "email": user.email,
        "region": user.region,
        "created_at": user.created_at.isoformat() if user.created_at else None
          }

class UserSearchResult(BaseModel):
    id: int
    name: Optional[str] = None
    email: str
    region: Optional[str] = None

class UserSearchResponse(BaseModel):
    users: List[UserSearchResult]

@router.get("/search", response_model=UserSearchResponse)
async def search_users(
    q: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Search users by name or email for send functionality"""
    
    if not q or len(q.strip()) < 2:
        return UserSearchResponse(users=[])
    
    try:
        # Get current user to exclude from results
        current_user_obj = db.query(User).filter(User.auth0_id == current_user.id).first()
        current_user_id = current_user_obj.id if current_user_obj else None
        
        search_term = f"%{q.strip()}%"
        
        # Join with bridge_customers to get name - using simpler approach
        query = db.query(User, BridgeCustomer).outerjoin(
            BridgeCustomer, User.id == BridgeCustomer.user_id
        ).filter(
            or_(
                func.lower(User.email).like(func.lower(search_term)),
                func.lower(BridgeCustomer.first_name).like(func.lower(search_term)),
                func.lower(BridgeCustomer.last_name).like(func.lower(search_term))
            )
        )
        
        # Exclude current user from results
        if current_user_id:
            query = query.filter(User.id != current_user_id)
        
        # Limit results to prevent overwhelming the UI
        user_results = query.limit(10).all()
        
        # Convert to response format
        results = []
        for user, bridge_customer in user_results:
            # Construct full name if available
            full_name = None
            if bridge_customer:
                if bridge_customer.first_name and bridge_customer.last_name:
                    full_name = f"{bridge_customer.first_name} {bridge_customer.last_name}"
                elif bridge_customer.first_name:
                    full_name = bridge_customer.first_name
            
            results.append(UserSearchResult(
                id=user.id,
                name=full_name,
                email=user.email,
                region=user.region
            ))
        
        return UserSearchResponse(users=results)
        
    except Exception as e:
        print(f"Search error: {e}")  # For debugging
        return UserSearchResponse(users=[]) 