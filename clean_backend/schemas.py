"""Pydantic schema definitions used by FastAPI routes.

This module deliberately avoids exposing internal SQLAlchemy objects to the
HTTP layer.  Each schema is a strict contract between API and client.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, condecimal, constr

# Existing schemas

class UserOut(BaseModel):
    """User data returned by auth/registration endpoints."""

    id: UUID
    email: constr(max_length=128)


class TOSAcceptedIn(BaseModel):
    signed_agreement_id: str


class RegisterIn(BaseModel):
    """Registration payload accepted by the onboarding route."""

    email: Optional[str] = Field(None, max_length=128)
    first_name: Optional[str] = Field(None, max_length=64)
    last_name: Optional[str] = Field(None, max_length=64)


#LATAM VelaFi integration schemas

class LatamKycStatus(str, Enum):
    PENDING = "pending"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"


class VelafiDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class VelafiStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class VelafiOrderSchema(BaseModel):
    """Read-only projection of a VelafiOrder row returned by admin APIs."""

    id: int
    order_id: constr(max_length=64)
    user_id: UUID

    direction: VelafiDirection

    fiat_amount: condecimal(max_digits=18, decimal_places=2)
    fiat_currency: constr(min_length=3, max_length=3)

    usdc_amount: Optional[condecimal(max_digits=18, decimal_places=2)]
    fx_rate: Optional[condecimal(max_digits=18, decimal_places=6)]
    fee_usd: Optional[condecimal(max_digits=18, decimal_places=2)]

    rail: Optional[constr(max_length=16)]
    status: VelafiStatus

    tx_hash: Optional[constr(max_length=66)]

    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # Allows FastAPI to serialise from SQLAlchemy objects 