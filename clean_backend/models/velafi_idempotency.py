from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, String, JSON, func, UniqueConstraint

from ..database import Base

class VelafiIdempotencyKey(Base):
    """Stores idempotency keys and cached JSON responses for replay safety."""

    __tablename__ = "velafi_idempotency_key"
    __table_args__ = (
        UniqueConstraint("key", name="uq_velafi_idempotency_key"),
    )

    id = Column(Integer, primary_key=True)
    key = Column(String(128), nullable=False)
    response_json = Column(JSON, nullable=True)
    status_code = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True) 