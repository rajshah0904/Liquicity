import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Numeric, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base

# --- ENUMS ---

class PaymentRail(enum.Enum):
    ACH = "ach"
    SEPA = "sepa"

class TransferType(enum.Enum):
    FIAT_DEPOSIT       = "fiat_deposit"      # Plaid → Bridge
    WALLET_DEPOSIT     = "wallet_deposit"    # External stablecoin → Bridge
    SEND               = "send"              # Bridge → Bridge
    WITHDRAWAL         = "withdrawal"        # Bridge → External bank or wallet
    EXTERNAL_TRANSFER  = "external_transfer" # External payout to user VA

class TransferStatus(enum.Enum):
    PENDING    = "pending"
    COMPLETED  = "completed"
    FAILED     = "failed"

class EncumbranceStatus(enum.Enum):
    PENDING = "pending"
    CLEARED = "cleared"
    FAILED  = "failed"

# VirtualAccountRole enum removed - no longer used in Bridge API structure



# --- CORE USER / KYC ---

class User(Base):
    __tablename__ = "users"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email      = Column(String(128), unique=True, nullable=False, index=True)
    auth0_id   = Column(String(64), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bridge_customer       = relationship("BridgeCustomer", uselist=False, back_populates="user")
    bridge_wallets        = relationship("BridgeWallet", back_populates="user")
    external_accounts     = relationship("ExternalAccount", back_populates="user")
    external_wallets      = relationship("ExternalWallet", back_populates="user")
    virtual_accounts      = relationship("VirtualAccount", back_populates="user")
    transfers             = relationship("Transfer", back_populates="user")
    liquidation_addresses = relationship("LiquidationAddress", back_populates="user")
    velafi_orders         = relationship("VelafiOrder", back_populates="user")


# --- BRIDGE CUSTOMER ---

class BridgeCustomer(Base):
    __tablename__ = "bridge_customers"
    id                              = Column(String(50), primary_key=True)  # Bridge customer ID (API: id)
    user_id                         = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    
    first_name                      = Column(String(1024))                  # Bridge API field
    last_name                       = Column(String(1024))                  # Bridge API field
    email                           = Column(String(1024))                  # Bridge API field
    status                          = Column(String(32))                    # Bridge API field
    
    # Address fields for KYC fallback (Bridge address spec format)
    street_line_1                   = Column(String(1024))                  # Bridge spec: required, length ≥ 4
    street_line_2                   = Column(String(1024))                  # Bridge spec: optional, length ≥ 1  
    city                            = Column(String(1024))                  # Bridge spec: required, length ≥ 1
    subdivision                     = Column(String(3))                     # Bridge spec: ISO 3166-2, length 1-3
    postal_code                     = Column(String(32))                    # Bridge spec: required for countries with postal codes
    country                         = Column(String(3))                     # Bridge spec: ISO 3166-1 alpha-3, length = 3
    capabilities                    = Column(JSON)                          # Bridge API JSON object
    future_requirements_due         = Column(JSON, default=[])              # Bridge API array
    requirements_due                = Column(JSON, default=[])              # Bridge API array
    created_at                      = Column(DateTime, nullable=False)      # Bridge API timestamp
    updated_at                      = Column(DateTime, nullable=False)      # Bridge API timestamp
    rejection_reasons               = Column(JSON, default=[])              # Bridge API array of objects
    has_accepted_terms_of_service   = Column(Boolean)                       # Bridge API field
    endorsements                    = Column(JSON, default=[])              # Bridge API array of objects
    requirements                    = Column(JSON)                          # Bridge API JSON object

    user                    = relationship("User", back_populates="bridge_customer")
    external_accounts       = relationship("ExternalAccount", back_populates="customer")
    bridge_wallets          = relationship("BridgeWallet", back_populates="customer")
    virtual_accounts        = relationship("VirtualAccount", back_populates="customer")

# --- WALLETS ---

class BridgeWallet(Base):
    __tablename__ = "bridge_wallets"
    wallet_id  = Column(String(50), primary_key=True)  # Bridge wallet ID from API
    customer_id= Column(String(50), ForeignKey("bridge_customers.id"), nullable=False)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    chain      = Column(String(32), nullable=False)  # e.g. "base", "solana"
    address    = Column(String(64), nullable=False)
    tags       = Column(JSON, default=[])  # Array of tags from Bridge API
    created_at = Column(DateTime)  # Bridge API timestamp
    updated_at = Column(DateTime)  # Bridge API timestamp
    balances   = Column(JSON, default=[])  # Array of balance objects from Bridge API

    customer = relationship("BridgeCustomer", back_populates="bridge_wallets")
    user     = relationship("User", back_populates="bridge_wallets")

class ExternalWallet(Base):
    __tablename__ = "external_wallets"
    external_wallet_id = Column(String(64), primary_key=True)  # e.g. wallet address
    customer_id        = Column(String(50), ForeignKey("bridge_customers.id"), nullable=False)
    user_id            = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    chain      = Column(String(32), nullable=False)
    address    = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="external_wallets")

# --- EXTERNAL ACCOUNTS (Bridge) ---

class ExternalAccount(Base):
    __tablename__ = "external_accounts"
    external_account_id  = Column(String(50), primary_key=True)  # Bridge external account ID from API
    customer_id          = Column(String(50), ForeignKey("bridge_customers.id"), nullable=False)
    user_id              = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    currency             = Column(String(8), nullable=False)     # "usd", "eur", "mxn"
    bank_name            = Column(String(256))                   # e.g. "Chase"
    account_owner_name   = Column(String(256), nullable=False)   # e.g. "John Doe" (first_name + " " + last_name)
    last_4               = Column(String(4))                     # Last 4 digits (deprecated but in API)                        # All account details (US/IBAN/CLABE/SWIFT) from Bridge API
    account_owner_type   = Column(String(32))                    # "individual", "business"
    business_name        = Column(String(256))                   # Business name for business accounts
    created_at           = Column(DateTime, nullable=False)      # Bridge API timestamp
    updated_at           = Column(DateTime, nullable=False)      # Bridge API timestamp
    active               = Column(Boolean, nullable=False)       # Bridge API active status                         # Google Maps or Plaid provided address

    plaid_item           = relationship("PlaidItem", uselist=False, back_populates="external_account")
    customer             = relationship("BridgeCustomer", back_populates="external_accounts")
    user                 = relationship("User", back_populates="external_accounts")

# --- PLAID ITEM ---

class PlaidItem(Base):
    __tablename__ = "plaid_items"
    plaid_item_id       = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_account_id = Column(String(50), ForeignKey("external_accounts.external_account_id"), nullable=False, unique=True)
    customer_id         = Column(String(50), ForeignKey("bridge_customers.id"), nullable=False)
    user_id             = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    access_token        = Column(String(128), nullable=False)
    item_id             = Column(String(64), nullable=False)    # Plaid Item ID from exchange response

    # Bridge timestamps to match external account lifecycle
    created_at          = Column(DateTime, nullable=False)      # From Bridge external account created_at
    updated_at          = Column(DateTime, nullable=False)      # From Bridge external account updated_at

    external_account    = relationship("ExternalAccount", back_populates="plaid_item")

# --- VIRTUAL ACCOUNTS (Bridge) ---

class VirtualAccount(Base):
    __tablename__ = "virtual_accounts"
    virtual_account_id        = Column(String(50), primary_key=True)  # Bridge virtual account ID from API
    customer_id               = Column(String(50), ForeignKey("bridge_customers.id"), nullable=False)
    user_id                   = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status                    = Column(String(16))                   # "activated", "deactivated"
    source_deposit_instructions = Column(JSON)                       # Complete deposit instructions object
    destination               = Column(JSON)                         # Destination crypto wallet info
    created_at                = Column(DateTime)                     # Created timestamp from Bridge API

    customer                  = relationship("BridgeCustomer", back_populates="virtual_accounts")
    user                      = relationship("User", back_populates="virtual_accounts")

# --- TRANSFERS & ENCUMBRANCE ---

class Transfer(Base):
    __tablename__ = "transfers"
    transfer_id = Column(String(50), primary_key=True)  # Bridge transfer ID
    customer_id = Column(String(50), ForeignKey("bridge_customers.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    client_reference_id = Column(String(256))                   # Bridge API field
    amount = Column(Numeric(18, 6), nullable=False)             # Decimal string from Bridge API
    currency = Column(String(8), nullable=False)                # Bridge API field
    on_behalf_of = Column(String(50), nullable=False)           # Bridge customer ID        
    developer_fee = Column(Numeric(18, 6), nullable=False)      # Decimal string from Bridge API
    source = Column(JSON, nullable=False, default=dict)         # Complete source object from Bridge API
    destination = Column(JSON, nullable=False, default=dict)    # Complete destination object from Bridge API
    state                     = Column(String(32), nullable=False)   # Bridge API state field
    status = Column(
        SQLEnum(TransferStatus, name="transfer_status"),
        nullable=False,
        default=TransferStatus.PENDING,
    )
    source_deposit_instructions = Column(JSON, default=dict)
    receipt = Column(JSON, nullable=False, default=dict)
    return_details = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user       = relationship("User", back_populates="transfers")
    encumbrances = relationship("Encumbrance", back_populates="transfer")

class Encumbrance(Base):
    __tablename__ = "encumbrances"
    encumbrance_id  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transfer_id     = Column(String(50), ForeignKey("transfers.transfer_id"), nullable=False)
    customer_id     = Column(String(50), ForeignKey("bridge_customers.id"), nullable=False)
    user_id         = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    original_amount = Column(Numeric(18,6), nullable=False)
    remaining_amount= Column(Numeric(18,6), nullable=False)
    status          = Column(SQLEnum(EncumbranceStatus), default=EncumbranceStatus.PENDING)
    cleared_at      = Column(DateTime)

    transfer        = relationship("Transfer", back_populates="encumbrances")
    created_at      = Column(DateTime, default=datetime.utcnow)
    updated_at      = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# --- WITHDRAWAL ADDRESSES ---

class LiquidationAddress(Base):
    __tablename__ = "liquidation_addresses"
    liquidation_address_id   = Column(String(50), primary_key=True)  # Bridge liquidation address ID from API
    customer_id              = Column(String(50), ForeignKey("bridge_customers.id"), nullable=False)
    user_id                  = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    currency                 = Column(String(8), nullable=False)     # Bridge API field
    chain                    = Column(String(32), nullable=False)    # Bridge API field
    external_account_id      = Column(String(50), nullable=False)    # Bridge API field
    prefunded_account_id     = Column(String(50))                    # Bridge API field
    destination_wire_message = Column(String(256))                   # Bridge API field
    destination_sepa_reference = Column(String(140))                 # Bridge API field
    destination_spei_reference = Column(String(40))                  # Bridge API field
    destination_ach_reference = Column(String(10))                   # Bridge API field
    destination_payment_rail = Column(String(32), nullable=False)    # Bridge API field
    destination_currency     = Column(String(8), nullable=False)     # Bridge API field
    address                  = Column(String(64), nullable=False)    # Bridge API field
    destination_address      = Column(String(64))                    # Bridge API field
    destination_blockchain_memo = Column(String(256))                # Bridge API field
    return_address           = Column(String(64))                    # Bridge API field
    state                    = Column(String(16))                    # Bridge API field
    created_at               = Column(DateTime, nullable=False)      # Bridge API timestamp
    updated_at               = Column(DateTime, nullable=False)      # Bridge API timestamp

    user     = relationship("User", back_populates="liquidation_addresses")


