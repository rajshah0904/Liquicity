"""SQLAlchemy models for VelaFi on-ramp tables.

These are *not* registered with Alembic yet. After finalising the columns,
create a migration under `alembic/versions/`.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Numeric, String, Enum as PgEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID

from clean_backend.database import Base  # reuse global metadata


class OnRampPaymentMethod(Base):
    __tablename__ = "onramp_payment_methods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False)
    payment_method_id = Column(String, unique=True, nullable=False)
    plaid_token_hash = Column(String, nullable=False)
    fiat_rail = Column(String, nullable=False)
    country = Column(String(2), nullable=False)
    currency = Column(String(3), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    raw_payload = Column(JSONB, nullable=True)


# Python Enum for status values
from enum import Enum as PyEnum


class OrderStatus(str, PyEnum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class OnRampOrder(Base):
    __tablename__ = "onramp_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False)
    payment_method_id = Column(UUID(as_uuid=True), nullable=False)
    velafi_order_id = Column(String, unique=True, nullable=False)
    fiat_amount = Column(Numeric, nullable=False)
    fiat_currency = Column(String(3), nullable=False)
    fiat_rail = Column(String, nullable=False)
    status = Column(PgEnum(OrderStatus, name="onramp_order_status"), default=OrderStatus.pending, nullable=False)
    usdc_amount = Column(Numeric, nullable=True)
    quote_rate = Column(Numeric, nullable=True)
    fee_usd = Column(Numeric, nullable=True)
    raw_payload = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False) 