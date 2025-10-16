"""
Minimal application settings.
Loads .env once and exposes only the options we actually use.
"""

import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from enum import Enum
from dotenv import load_dotenv

# Load .env process-wide as early as possible
load_dotenv()


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")

    # API server
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")

    # Database
    database_url: str = Field(
        default="postgresql://liquicity_user:Liquicity2025!@localhost:5432/liquicity_db",
        env="DATABASE_URL",
    )

    # Bridge
    bridge_api_key: str = Field(default=os.getenv("BRIDGE_API_KEY", ""), env="BRIDGE_API_KEY")
    bridge_base_url: str = Field(default=os.getenv("BRIDGE_API_URL", "https://api.bridge.xyz/v0"), env="BRIDGE_API_URL")

    # Treasury
    treasury_customer_id: str = Field(default=os.getenv("TREASURY_CUSTOMER_ID", ""), env="TREASURY_CUSTOMER_ID")
    treasury_wallet_id: str = Field(default=os.getenv("TREASURY_WALLET_ID", ""), env="TREASURY_WALLET_ID")

    # CORS
    cors_origins: List[str] = Field(default=["http://localhost:3000"], env="CORS_ORIGINS")

    # Plaid EU configuration (non-secret; secrets come from env via PlaidClient)
    plaid_country_codes_eu: List[str] = Field(default=["GB","IE","FR","DE","ES","NL","IT"], env="PLAID_COUNTRY_CODES_EU")

    # Corporate EU VA details (placeholder; required to enable EU payments)
    corporate_eu_va_iban: str = Field(default=os.getenv("CORPORATE_EU_VA_IBAN", ""), env="CORPORATE_EU_VA_IBAN")
    corporate_eu_va_bic: str = Field(default=os.getenv("CORPORATE_EU_VA_BIC", ""), env="CORPORATE_EU_VA_BIC")
    corporate_eu_va_name: str = Field(default=os.getenv("CORPORATE_EU_VA_NAME", "Liquicity Treasury EU"), env="CORPORATE_EU_VA_NAME")


# Singleton settings object
settings = Settings() 