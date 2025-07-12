from sqlalchemy import Column, String, DateTime, Enum, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base

class WalletSession(Base):
    __tablename__ = "wallet_sessions"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    wallet_address = Column(String, nullable=True)
    chain_type = Column(String)
    chain_id = Column(String)
    status = Column(String, index=True)
    topic = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    approved_at = Column(DateTime, nullable=True)
    disconnected_at = Column(DateTime, nullable=True)

    transfers = relationship("USDCPayment", back_populates="session")


class USDCPayment(Base):
    __tablename__ = "usdc_transfers"
    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("wallet_sessions.id"))
    from_address = Column(String)
    to_address = Column(String)
    amount = Column(Numeric(asdecimal=False))
    chain_type = Column(String)
    chain_id = Column(String)
    currency = Column(String)
    status = Column(String, index=True)
    transaction_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("WalletSession", back_populates="transfers") 