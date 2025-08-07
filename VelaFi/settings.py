"""
Production Configuration Settings
Comprehensive configuration management with validation
"""

import os
from typing import Dict, List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.types import SecretStr
from enum import Enum
from decimal import Decimal

# Load environment variables from .env file at project root
from dotenv import load_dotenv
load_dotenv('.env')

print("WALLETCONNECT_PROJECT_ID from env:", os.environ.get("WALLETCONNECT_PROJECT_ID"))

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class NetworkConfig(str, Enum):
    POLYGON = "polygon"
    BASE = "base"
    SOLANA = "solana"
    ETHEREUM = "ethereum"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"

class SecurityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Settings(BaseSettings):
    # Pydantic (v2) model configuration
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding="utf-8",
        extra="allow",  # ignore extra vars present in .env
    )

    # Environment
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_workers: int = Field(default=4, env="API_WORKERS")
    api_timeout: int = Field(default=30, env="API_TIMEOUT")
    
    # Security
    secret_key: SecretStr = Field("dev-secret-key-please-change-me-1234567890", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour
    
    # WalletConnect Configuration
    walletconnect_project_id: str = Field("dev-walletconnect-project", env="WALLETCONNECT_PROJECT_ID")
    walletconnect_relay_url: str = Field(default="wss://relay.walletconnect.com", env="WALLETCONNECT_RELAY_URL")
    walletconnect_metadata: Dict = Field(default={
        "name": "Liquicity Bridge",
        "description": "Cross-border crypto payments",
        "url": "https://liquicity.com",
        "icons": ["https://liquicity.com/icon.png"]
    })
    
    # Bridge API Configuration
    bridge_api_key: SecretStr = Field("dev-bridge-api-key", env="BRIDGE_API_KEY")
    bridge_base_url: str = Field(default="https://api.bridge.xyz/v0", env="BRIDGE_BASE_URL")
    bridge_timeout: int = Field(default=30, env="BRIDGE_TIMEOUT")
    bridge_retry_attempts: int = Field(default=3, env="BRIDGE_RETRY_ATTEMPTS")

    # VelaFi Configuration
    velafi_api_key: SecretStr = Field("dev-velafi-api-key", env="VELAFI_API_KEY")
    velafi_base_url: str = Field(default="https://api.velafi.com", env="VELAFI_BASE_URL")
    velafi_webhook_secret: SecretStr = Field("dev-webhook-secret", env="VELAFI_WEBHOOK_SECRET")

    # On-ramp risk & compliance thresholds
    onramp_daily_limit_usd: Decimal = Field(default=Decimal("3000"), env="ONRAMP_DAILY_LIMIT_USD")
    onramp_risk_forward: bool = Field(default=False, env="ONRAMP_RISK_FORWARD")
    
    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_password: Optional[SecretStr] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    
    # Network Configurations
    networks: Dict[str, Dict] = Field(default={
        "polygon": {
            "chain_id": 137,
            "rpc_url": "https://polygon-rpc.com",
            "explorer": "https://polygonscan.com",
            "gas_price": 30000000000,  # 30 gwei
            "gas_limit": 21000,
            "max_priority_fee": 1500000000,  # 1.5 gwei
            "block_time": 2,
            "confirmations": 12
        },
        "base": {
            "chain_id": 8453,
            "rpc_url": "https://mainnet.base.org",
            "explorer": "https://basescan.org",
            "gas_price": 1500000000,  # 1.5 gwei
            "gas_limit": 21000,
            "max_priority_fee": 100000000,  # 0.1 gwei
            "block_time": 2,
            "confirmations": 12
        },
        "solana": {
            "chain_id": "solana:mainnet",
            "rpc_url": "https://api.mainnet-beta.solana.com",
            "explorer": "https://solscan.io",
            "gas_price": 5000,  # 5000 lamports
            "gas_limit": 1,
            "max_priority_fee": 0,
            "block_time": 0.4,
            "confirmations": 32
        },
        "ethereum": {
            "chain_id": 1,
            "rpc_url": "https://eth-mainnet.alchemyapi.io/v2/your-key",
            "explorer": "https://etherscan.io",
            "gas_price": 20000000000,  # 20 gwei
            "gas_limit": 21000,
            "max_priority_fee": 2000000000,  # 2 gwei
            "block_time": 12,
            "confirmations": 12
        },
        "arbitrum": {
            "chain_id": 42161,
            "rpc_url": "https://arb1.arbitrum.io/rpc",
            "explorer": "https://arbiscan.io",
            "gas_price": 100000000,  # 0.1 gwei
            "gas_limit": 21000,
            "max_priority_fee": 100000000,  # 0.1 gwei
            "block_time": 1,
            "confirmations": 12
        },
        "optimism": {
            "chain_id": 10,
            "rpc_url": "https://mainnet.optimism.io",
            "explorer": "https://optimistic.etherscan.io",
            "gas_price": 1000000,  # 0.001 gwei
            "gas_limit": 21000,
            "max_priority_fee": 1000000,  # 0.001 gwei
            "block_time": 2,
            "confirmations": 12
        }
    })
    
    # Payment Configuration
    min_payment_amount: float = Field(default=0.01, env="MIN_PAYMENT_AMOUNT")
    max_payment_amount: float = Field(default=100000.0, env="MAX_PAYMENT_AMOUNT")
    default_currency: str = Field(default="usdc", env="DEFAULT_CURRENCY")
    supported_currencies: List[str] = Field(default=["usdc", "usdt", "dai"], env="SUPPORTED_CURRENCIES")
    
    # Session Configuration
    session_expiry_hours: int = Field(default=24, env="SESSION_EXPIRY_HOURS")
    consent_expiry_minutes: int = Field(default=30, env="CONSENT_EXPIRY_MINUTES")
    max_sessions_per_user: int = Field(default=5, env="MAX_SESSIONS_PER_USER")
    
    # Monitoring and Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    # Security Settings
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    enable_rate_limiting: bool = Field(default=True, env="ENABLE_RATE_LIMITING")
    enable_ssl: bool = Field(default=False, env="ENABLE_SSL")
    ssl_cert_path: Optional[str] = Field(default=None, env="SSL_CERT_PATH")
    ssl_key_path: Optional[str] = Field(default=None, env="SSL_KEY_PATH")
    
    # Encryption
    encryption_key: SecretStr = Field("dev-encryption-key-please-change-1234567890", env="ENCRYPTION_KEY")
    encryption_algorithm: str = Field(default="AES-256-GCM", env="ENCRYPTION_ALGORITHM")
    
    # Webhook Configuration
    webhook_secret: Optional[SecretStr] = Field(default=None, env="WEBHOOK_SECRET")
    webhook_timeout: int = Field(default=10, env="WEBHOOK_TIMEOUT")
    
    # Compliance and KYC
    enable_kyc: bool = Field(default=True, env="ENABLE_KYC")
    kyc_provider: str = Field(default="sumsub", env="KYC_PROVIDER")
    kyc_api_key: Optional[SecretStr] = Field(default=None, env="KYC_API_KEY")
    
    # Risk Management
    enable_risk_checks: bool = Field(default=True, env="ENABLE_RISK_CHECKS")
    max_daily_transactions: int = Field(default=1000, env="MAX_DAILY_TRANSACTIONS")
    suspicious_amount_threshold: float = Field(default=10000.0, env="SUSPICIOUS_AMOUNT_THRESHOLD")

# Instantiate the settings object
settings = Settings()