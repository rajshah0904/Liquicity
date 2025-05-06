from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, JSON, Table
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
from typing import Dict, List, Any

# Association table for team members
team_members = Table(
    "team_members",
    Base.metadata,
    Column("team_id", Integer, ForeignKey("teams.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    wallet_address = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    # OAuth and verification fields
    google_id = Column(String, unique=True, nullable=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    verification_token_expires_at = Column(DateTime, nullable=True)
    reset_password_token = Column(String, nullable=True)
    reset_password_token_expires_at = Column(DateTime, nullable=True)
    role = Column(String, default="user")  # admin, user, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Personal information
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)
    country = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    ssn = Column(String, nullable=True)
    
    # Address information
    street_address = Column(String, nullable=True)
    street_address_2 = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    address_country = Column(String, nullable=True)
    
    # Stripe and payment info
    stripe_customer_id = Column(String, nullable=True)

    # Relationships - Basic single relationship
    wallet = relationship("Wallet", back_populates="owner", uselist=False)
    
    # User-to-Transaction relationships with explicit foreign keys
    # These cannot be named 'transactions_sent' and 'transactions_received'
    # to avoid SQLAlchemy conflicts with multiple foreign keys
    sent_txns = relationship(
        "Transaction", 
        foreign_keys="[Transaction.sender_id]",
        primaryjoin="User.id==Transaction.sender_id",
        back_populates="sender"
    )
    
    received_txns = relationship(
        "Transaction", 
        foreign_keys="[Transaction.recipient_id]",
        primaryjoin="User.id==Transaction.recipient_id",
        back_populates="recipient"
    )
    
    # Trade relationships with explicit foreign keys
    trade_sent = relationship(
        "Trade", 
        foreign_keys="[Trade.sender_id]",
        primaryjoin="User.id==Trade.sender_id",
        back_populates="sender"
    )
    
    trade_received = relationship(
        "Trade", 
        foreign_keys="[Trade.recipient_id]",
        primaryjoin="User.id==Trade.recipient_id",
        back_populates="recipient"
    )
    
    # Other relationships
    teams = relationship("Team", secondary=team_members, back_populates="members")
    user_metadata = relationship("UserMetadata", back_populates="user", uselist=False)
    bank_accounts = relationship("BankAccount", back_populates="user")

class UserMetadata(Base):
    __tablename__ = "user_metadata"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)  # Store as ISO format string
    country = Column(String, nullable=True)
    country_code = Column(String, nullable=True)  # 2-letter country code
    id_number = Column(String, nullable=True)  # SSN, NIN, etc.
    id_type = Column(String, nullable=True)  # Type of ID (SSN, Passport, etc.)
    document_type = Column(String, nullable=True)
    document_number = Column(String, nullable=True)
    address_street = Column(String, nullable=True)
    address_city = Column(String, nullable=True)
    address_state = Column(String, nullable=True)
    address_postal = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    verification_status = Column(String, default="unverified")  # unverified, pending, verified, rejected
    verified_at = Column(DateTime, nullable=True)
    profile_data = Column(JSON, nullable=True)  # Additional profile information
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="user_metadata")

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    members = relationship("User", secondary=team_members, back_populates="teams")

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    recipient_id = Column(Integer, ForeignKey("users.id"))
    stablecoin_amount = Column(Float, nullable=False)
    fiat_amount = Column(Float, nullable=False)
    conversion_rate = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")

    # Relationships with explicit foreign keys
    sender = relationship(
        "User", 
        foreign_keys=[sender_id],
        primaryjoin="Trade.sender_id==User.id",
        back_populates="trade_sent"
    )
    
    recipient = relationship(
        "User", 
        foreign_keys=[recipient_id],
        primaryjoin="Trade.recipient_id==User.id",
        back_populates="trade_received"
    )

class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    fiat_balance = Column(Float, default=0.0)
    
    # Primary currency of the wallet (user's local currency)
    base_currency = Column(String, default="USD")
    
    # User's preferred display currency (can differ from base)
    display_currency = Column(String, default="USD")
    
    # Country code to help with regulatory compliance
    country_code = Column(String, nullable=True)
    
    # JSON field to store additional currency information
    currency_settings = Column(JSON, nullable=True)

    # Simple relationship with User model
    owner = relationship("User", back_populates="wallet")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    recipient_id = Column(Integer, ForeignKey("users.id"))
    stablecoin_amount = Column(Float)
    source_amount = Column(Float)
    source_currency = Column(String)
    target_amount = Column(Float)
    target_currency = Column(String)
    source_to_stablecoin_rate = Column(Float)
    stablecoin_to_target_rate = Column(Float)
    status = Column(String, default="pending")
    blockchain_txn_hash = Column(String, nullable=True)  # For on-chain transactions
    timestamp = Column(DateTime, default=datetime.utcnow)
    payment_source = Column(String, nullable=True)  # wallet, card, bank, wallet_partial
    transaction_type = Column(String, default="TRANSFER")  # TRANSFER, CARD_PAYMENT, BANK_PAYMENT, etc.
    
    # Clear relationship definitions with foreign keys
    sender = relationship(
        "User", 
        foreign_keys=[sender_id],
        primaryjoin="Transaction.sender_id==User.id",
        back_populates="sent_txns"
    )
    
    recipient = relationship(
        "User", 
        foreign_keys=[recipient_id],
        primaryjoin="Transaction.recipient_id==User.id",
        back_populates="received_txns"
    )

class BankAccount(Base):
    __tablename__ = "bank_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stripe_bank_id = Column(String, unique=True, index=True)
    bank_name = Column(String)
    account_type = Column(String)  # checking, savings, etc.
    last4 = Column(String)  # Last 4 digits of account number
    country = Column(String)
    currency = Column(String)
    status = Column(String, default="active")  # active, deleted, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    bank_metadata = Column(Text, nullable=True)  # JSON encoded metadata
    
    user = relationship("User", back_populates="bank_accounts")
