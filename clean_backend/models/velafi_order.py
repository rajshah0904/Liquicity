"""VelafiOrder SQLAlchemy model representing LATAM on/off-ramp orders handled by VelaFi.

A separate file keeps the LATAM-specific integration isolated from the core Bridge
models defined in `clean_backend/models.py`.
"""
import enum

# Note: no direct datetime usage required here; timestamps come from SQL defaults
from sqlalchemy import (
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

    # Align with root Alembic schema: UUID primary key
    id = Column(UUID(as_uuid=True), primary_key=True)
    # Keep Python attribute name `order_id`, map to DB column `velafi_order_id`
    order_id = Column("velafi_order_id", String(64), unique=True, nullable=False, index=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User", back_populates="velafi_orders")

    # Note: Root schema may not include `direction`. Retained here for app logic;
    # migration alignment to be finalized in a follow-up if needed.
    direction = Column(SQLEnum(VelafiDirection, name="velafi_direction"), nullable=False)

    fiat_amount = Column(Numeric(18, 2), nullable=False)
    fiat_currency = Column(String(3), nullable=False)

    usdc_amount = Column(Numeric(18, 2))
    fx_rate = Column(Numeric(18, 6))
    fee_usd = Column(Numeric(18, 2))

    rail = Column(String(16))  # pix, spei, cbu, etc.
    # Use existing DB enum name from root Alembic: velafi_order_status
    status = Column(
        SQLEnum(VelafiStatus, name="velafi_order_status"),
        nullable=False,
        server_default=VelafiStatus.PENDING.value,
    )

    tx_hash = Column(String(66))  # 0x-prefixed Ethereum tx hash (or similar)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<VelafiOrder order_id={self.order_id} status={self.status}>"