from __future__ import annotations

import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base

class PlaidItem(Base):
    """Stores Plaid access tokens (one per external account)."""

    __tablename__ = "plaid_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # One-to-one link to Bridge external account
    external_account_id = Column(
        String(64), ForeignKey("external_accounts_v2.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    access_token = Column(String, nullable=False)
    item_id = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationship back to ExternalAccount
    external_account = relationship("ExternalAccount", back_populates="plaid_item") 