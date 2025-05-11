from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, JSON, Table
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

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
    email = Column(String, unique=True, index=True)
    auth0_id = Column(String, unique=True, nullable=True, index=True)
    is_verified = Column(Boolean, default=False)
    account_type = Column(String, nullable=True, default="auth0")
    # Bridge integration fields
    bridge_customer_id = Column(String, unique=True, nullable=True, index=True)
    kyc_status = Column(String, nullable=True)  # pending / approved / rejected
    endorsement_status = Column(JSON, nullable=True)
    role = Column(String, default="user")
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Personal information
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)
    country = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    
    # KYC fields
    id_number = Column(String, nullable=True)
    id_type = Column(String, nullable=True)
    document_type = Column(String, nullable=True)
    document_number = Column(String, nullable=True)
    country_code = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    verification_status = Column(String, default="unverified")
    verified_at = Column(DateTime, nullable=True)
    
    # Address information
    address_line1 = Column(String, nullable=True)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    
    wallet_address = Column(String, nullable=True)

    # Relationships
    wallet = relationship("Wallet", back_populates="owner", uselist=False)
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
    teams = relationship("Team", secondary=team_members, back_populates="members")
    bank_accounts = relationship("BankAccount", back_populates="user")

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    members = relationship("User", secondary=team_members, back_populates="teams")

class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    fiat_balance = Column(Float, default=0.0)
    base_currency = Column(String, default="USD")
    display_currency = Column(String, default="USD")
    country_code = Column(String, nullable=True)
    currency_settings = Column(JSON, nullable=True)
    owner = relationship("User", back_populates="wallet")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    recipient_id = Column(Integer, ForeignKey("users.id"))
    source_amount = Column(Float)
    source_currency = Column(String)
    target_amount = Column(Float)
    target_currency = Column(String)
    status = Column(String, default="pending")
    timestamp = Column(DateTime, default=datetime.utcnow)
    payment_source = Column(String, nullable=True)
    transaction_type = Column(String, default="TRANSFER")
    
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
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    mt_account_id = Column(String, unique=True, index=True)
    brale_account_id = Column(String, unique=True, index=True)
    bank_name = Column(String)
    account_type = Column(String)
    last4 = Column(String)
    country = Column(String)
    currency = Column(String)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    bank_metadata = Column(Text)
    
    user = relationship("User", back_populates="bank_accounts")

# NOTE: Legacy KycData model removed in favour of storing only Bridge metadata on Users.
