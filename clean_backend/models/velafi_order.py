"""VelafiOrder SQLAlchemy model representing LATAM on/off-ramp orders handled by VelaFi.

A separate file keeps the LATAM-specific integration isolated from the core Bridge
models defined in `clean_backend/models.py`.
"""
import enum
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class VelafiDirection(enum.Enum):
    BUY = "BUY"   # Fiat -> USDC (deposit)
    SELL = "SELL"  # USDC -> Fiat (withdraw)


class VelafiStatus(enum.Enum):
    PENDING = "pending"       #Order created, waiting for fiat
    PROCESSING = "processing" #Fiat received -> FX + mint now
    COMPLETED = "completed"   #USDC on-chain sent
    FAILED = "failed"         #Rejected or funding failed
    PARTIAL = "partial"       #Over/under-payment outside tolerance


class VelafiOrder(Base):
    __tablename__ = "velafi_orders"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(String(64), unique=True, nullable=False, index=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User", back_populates="velafi_orders")

    direction = Column(SQLEnum(VelafiDirection), nullable=False)

    fiat_amount = Column(Numeric(18, 2), nullable=False)
    fiat_currency = Column(String(3), nullable=False)

    usdc_amount = Column(Numeric(18, 2))
    fx_rate = Column(Numeric(18, 6))
    fee_usd = Column(Numeric(18, 2))

    rail = Column(String(16))  # pix, spei, cbu, etc.
    status = Column(SQLEnum(VelafiStatus), nullable=False, default=VelafiStatus.PENDING)

    tx_hash = Column(String(66))  # 0x-prefixed Ethereum tx hash (or similar)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<VelafiOrder order_id={self.order_id} status={self.status}>"