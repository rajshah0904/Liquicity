import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default to Google Cloud PostgreSQL via proxy, but allow override via environment variable
# Development: Uses Cloud SQL Proxy (localhost:5432 -> Google Cloud SQL)
# Production: Direct connection to Google Cloud PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://liquicity_user:Liquicity2025!@localhost:5432/liquicity_db")

# Database connection configuration
def create_database_engine():
    """Create database engine with appropriate configuration for PostgreSQL/Google Cloud SQL"""
    
    # PostgreSQL configuration (including Google Cloud SQL)
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=int(os.getenv("DATABASE_POOL_SIZE", "20")),
        max_overflow=int(os.getenv("DATABASE_MAX_OVERFLOW", "30")),
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=3600,   # Recycle connections every hour
        echo=os.getenv("DEBUG", "false").lower() == "true",
        # SSL configuration for Google Cloud SQL
        connect_args={
            "sslmode": "prefer"  # Prefer SSL but allow non-SSL for Cloud SQL Proxy
        }
    )
    
    return engine

engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ---- one-time schema check ----
def _ensure_schema():
    """Ensure required schema modifications are applied"""
    with engine.begin() as conn:
        try:
            # Check if we're connected to PostgreSQL
            result = conn.execute(text("SELECT version()"))
            logger.info(f"Connected to: {result.scalar()}")
            
            # Note: bridge_users_v2 table no longer exists in current schema
            # Schema modifications removed as they were for legacy database structure
            logger.info("Schema check completed successfully")
        except Exception as e:
            logger.warning(f"Schema check failed (this is normal for new databases): {e}")

# Run schema check
_ensure_schema()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

def create_tables():
    """Create all tables - should be called after models are imported"""
    try:
        # Import models here to avoid circular imports
        from .models import Base as ModelsBase
        ModelsBase.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.warning(f"Table auto-creation failed: {e}") 