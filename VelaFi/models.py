"""SQLAlchemy models for VelaFi integration (payment methods & orders)."""

from __future__ import annotations

import enum
import uuid
from decimal import Decimal
from typing import Any, Dict, Optional

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import Enum as PgEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from clean_backend.database import Base


class OrderStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class VelafiPaymentMethod(Base):
    __tablename__ = "velafi_payment_methods"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    payment_method_id = Column(String, unique=True, nullable=False)  # pm_*
    plaid_token_hash = Column(String(64), nullable=True)
    fiat_rail = Column(String(16))
    country = Column(String(2))
    currency = Column(String(3))
    raw_payload = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class VelafiOrder(Base):
    __tablename__ = "velafi_orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    payment_method_db_id = Column(UUID(as_uuid=True), ForeignKey("velafi_payment_methods.id"), nullable=True)
    velafi_order_id = Column(String, unique=True, nullable=False)  # ord_*
    fiat_amount = Column(Numeric(20, 2), nullable=False)
    fiat_currency = Column(String(3), default="USD")
    status = Column(PgEnum(OrderStatus, name="velafi_order_status"), nullable=False, default=OrderStatus.pending)
    usdc_amount = Column(Numeric(20, 6))
    quote_rate = Column(Numeric(20, 8))
    fee_usd = Column(Numeric(20, 2))
    raw_payload = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("velafi_order_id", name="uq_velafi_order_id"),
    )

# ------------------------- VelaFi KYC Models -------------------------

class VelafiCustomer(Base):
    """VelaFi customer record for KYC purposes."""
    __tablename__ = "velafi_customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users_v2.id"), nullable=False, unique=True)
    velafi_customer_id = Column(String(64), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    date_of_birth = Column(String(10), nullable=False)  # YYYY-MM-DD format
    country = Column(String(2), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    kyc_status = Column(String(20), default="pending")  # pending, submitted, approved, rejected, under_review
    kyc_submitted_at = Column(DateTime(timezone=True), nullable=True)
    kyc_verified_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reasons = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="velafi_customer")
    documents = relationship("VelafiKycDocument", back_populates="customer", cascade="all, delete-orphan")


class VelafiKycDocument(Base):
    """VelaFi KYC document metadata."""
    __tablename__ = "velafi_kyc_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    velafi_customer_id = Column(UUID(as_uuid=True), ForeignKey("velafi_customers.id"), nullable=False)
    velafi_document_id = Column(String(64), unique=True, nullable=False)
    document_type = Column(String(50), nullable=False)  # passport, national_id, drivers_license, proof_of_address
    filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(String(20), default="uploaded")  # uploaded, verified, rejected
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Relationships
    customer = relationship("VelafiCustomer", back_populates="documents") 