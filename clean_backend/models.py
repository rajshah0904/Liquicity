from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Boolean, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.types import Numeric

class User(Base):
    __tablename__ = "users_v2"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    auth0_id = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    kyc_status = Column(String(20), default="pending")
    tos_status = Column(String(20), default="pending")  # pending, approved
    kyc_link_id = Column(String(64))
    kyc_type = Column(String(32))
    country = Column(String(64))  
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    bridge_customer_id = Column(String(64), unique=True)
    bridge_wallet_id = Column(String(64), unique=True)  # New column for Bridge wallet id
    tos_url = Column(String)
    kyc_url = Column(String)
    rejection_reasons = Column(String)

    # One-to-one relationship with BridgeUser helper table
    bridge_data = relationship(
        "BridgeUser",
        uselist=False,
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # New: one-to-many relationship to track the user's linked bank accounts
    external_accounts = relationship(
        "ExternalAccount",
        back_populates="user",
        cascade="all, delete-orphan",
    )



# ------------------- Bridge specific -------------------

class BridgeUser(Base):
    """Track Bridge customer & wallet ids for each Liquicity user (one-row per user)."""

    __tablename__ = "bridge_users_v2"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users_v2.id", ondelete="CASCADE"),
        primary_key=True,
    )
    bridge_customer_id = Column(String(64), unique=True)
    bridge_wallet_id = Column(String(64), unique=True)
    virtual_account_id = Column(String(64), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationship back to User
    user = relationship("User", back_populates="bridge_data")



# ------------------- External accounts -------------------

class ExternalAccount(Base):
    """Stores non-sensitive metadata about a user's connected bank/external account (Bridge)."""

    __tablename__ = "external_accounts_v2"

    # Use Bridge external account id as the primary key – it is a string
    id = Column(String(64), primary_key=True, index=True)

    # FK to Liquicity user
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users_v2.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Display-only information (no sensitive data stored)
    bank_name = Column(String(255))
    last4 = Column(String(4))
    currency = Column(String(16))
    status = Column(String(32))  # active, inactive, pending, etc.

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationship back to User
    user = relationship("User", back_populates="external_accounts")



# ------------------- Encumbrance tracking -------------------

class Encumbrance(Base):
    """One row per fiat transfer that was advanced on-chain."""

    __tablename__ = "encumbrances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fiat_transfer_id = Column(String(64), unique=True, nullable=False, index=True)
    original_amount = Column(Numeric(18, 6), nullable=False)
    recovered_amount = Column(Numeric(18, 6), default=0)
    status = Column(String(16), default="pending")  # pending | cleared | failed_*
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationship to current positions (encumbered balances still outstanding)
    positions = relationship(
        "EncPosition", back_populates="encumbrance", cascade="all, delete-orphan"
    )


class EncPosition(Base):
    """Current holders of an encumbrance (live 'UTXOs')."""

    __tablename__ = "encumbrance_positions"

    enc_id = Column(
        UUID(as_uuid=True),
        ForeignKey("encumbrances.id", ondelete="CASCADE"),
        primary_key=True,
    )
    wallet_id = Column(String(64), primary_key=True)
    amount = Column(Numeric(18, 6), nullable=False)
    last_updated = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    encumbrance = relationship("Encumbrance", back_populates="positions")


class WalletConnectSession(Base):
    __tablename__ = "walletconnect_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users_v2.id", ondelete="CASCADE"), nullable=False, index=True)
    wallet_address = Column(String(128), nullable=False)
    chain_type = Column(String(16), nullable=False)
    chain_id = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False, index=True)  # pending, approved, rejected, expired, disconnected
    topic = Column(String(128), unique=True, nullable=False, index=True)
    sym_key = Column(String(128), nullable=False)
    relay_protocol = Column(String(32), nullable=False, default="irn")
    version = Column(String(8), nullable=False, default="2")
    peer_metadata = Column(String, nullable=True)  # JSON as string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    disconnected_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User")


