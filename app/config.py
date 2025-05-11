import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Dict, List, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache

# Load environment variables
load_dotenv()

class DatabaseConfig(BaseModel):
    url: str = os.getenv("DATABASE_URL", "postgresql://raj:Rajshah11@localhost:5432/liquicity")

class AuthConfig(BaseModel):
    secret_key: str = os.getenv("SECRET_KEY", "your_secret_key_here")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    # Auth0 configuration
    auth0_domain: str = os.getenv("AUTH0_DOMAIN", "")
    auth0_client_id: str = os.getenv("AUTH0_CLIENT_ID", "")
    auth0_client_secret: str = os.getenv("AUTH0_CLIENT_SECRET", "")
    auth0_audience: str = os.getenv("AUTH0_AUDIENCE", "https://api.liquicity.io")
    auth0_callback_url: str = os.getenv("AUTH0_CALLBACK_URL", "http://localhost:8000/callback")

class DataStorageConfig(BaseModel):
    vector_db_path: str = os.getenv("VECTOR_DB_PATH", "./vector_db")
    data_storage_path: str = os.getenv("DATA_STORAGE_PATH", "./data_storage")

class AppConfig(BaseModel):
    database: DatabaseConfig = DatabaseConfig()
    auth: AuthConfig = AuthConfig()
    data_storage: DataStorageConfig = DataStorageConfig()
    debug: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    environment: str = os.getenv("ENVIRONMENT", "development")

# Create a global config instance
config = AppConfig()

def get_config() -> AppConfig:
    """Returns the application configuration."""
    return config 

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Auth0 Configuration
    AUTH0_DOMAIN: str
    AUTH0_CLIENT_ID: str
    AUTH0_CLIENT_SECRET: str
    AUTH0_AUDIENCE: str

    # Modern Treasury Configuration
    MODERN_TREASURY_API_KEY: str
    MODERN_TREASURY_ORGANIZATION_ID: str
    MODERN_TREASURY_ENVIRONMENT: str = "sandbox"

    # Brale Configuration
    BRALE_API_KEY: str
    BRALE_ENVIRONMENT: str = "sandbox"

    # Application Settings
    APP_URL: str = "http://localhost:3000"
    API_URL: str = "http://localhost:8000"
    NODE_ENV: str = "development"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings() 