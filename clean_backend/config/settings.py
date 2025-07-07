import os
from typing import Dict, List, Optional
from pydantic import BaseSettings, Field
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    walletconnect_project_id: str = Field(..., env="WALLETCONNECT_PROJECT_ID")
    walletconnect_relay_url: str = Field(default="wss://relay.walletconnect.com", env="WALLETCONNECT_RELAY_URL")
    walletconnect_metadata: Dict = Field(default={
        "name": "Liquicity Bridge",
        "description": "Cross-border crypto payments",
        "url": "https://liquicity.com",
        "icons": ["https://liquicity.com/icon.png"]
    })
    session_expiry_hours: int = Field(default=24, env="SESSION_EXPIRY_HOURS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

def get_settings() -> Settings:
    return Settings()

ERROR_CODES = {
    "INVALID_WALLET_ADDRESS": "invalid_wallet_address",
    "INVALID_NETWORK": "invalid_network",
    "SESSION_EXPIRED": "session_expired",
    "INTERNAL_ERROR": "internal_error"
} 