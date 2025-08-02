from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..auth import get_current_user
from pydantic import BaseModel, constr
from typing import Optional

router = APIRouter(prefix="/user", tags=["user"])

ALLOWED_COUNTRIES = [
    # USA & major
    "United States",
    "Mexico",
    "India",
    # SEPA countries
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "Malta", "Monaco", "Netherlands", "Norway", "Poland", "Portugal", "Romania", "San Marino", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "United Kingdom", "Andorra", "Vatican City"
]

class CountryIn(BaseModel):
    country: constr(min_length=2, max_length=64)

@router.get("/countries")
async def list_countries():
    return ALLOWED_COUNTRIES

@router.post("/country")
async def set_country(payload: CountryIn, db: Session = Depends(get_db), jwt=Depends(get_current_user)):
    country_name = payload.country.title()
    if country_name not in ALLOWED_COUNTRIES:
        raise HTTPException(status_code=400, detail="Unsupported country")
    user = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Note: country field removed from User model
    # For now, just return success - country selection is handled by Bridge during KYC
    return {"country": country_name, "status": "selected"}

@router.get("")
async def get_profile(db: Session = Depends(get_db), jwt=Depends(get_current_user)):
    """Return the authenticated user's basic profile (id, email, country)."""
    user: Optional[User] = db.query(User).filter(User.auth0_id == jwt.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": str(user.id),
        "email": user.email,
        "country": getattr(user, 'country', None),
    } 