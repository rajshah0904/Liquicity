import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ---- one-time schema tweak (adds virtual_account_id if missing) ----
def _ensure_schema():
    with engine.begin() as conn:
        try:
            conn.execute(text("""
                ALTER TABLE bridge_users_v2
                ADD COLUMN IF NOT EXISTS virtual_account_id varchar(64) UNIQUE
            """))
        except Exception:
            # Ignore if dialect or permissions don't support; runtime errors will surface elsewhere
            pass

_ensure_schema()

# Auto-create tables in non-prod dev environments (SQLite / local Postgres).
# In production this should be handled by Alembic migrations.
from .models import Base as _ModelsBase  # noqa

try:
    _ModelsBase.metadata.create_all(bind=engine)
except Exception as _e:
    # Log but don't crash – if migrations handle this it's okay
    import logging
    logging.getLogger(__name__).warning("Table auto-creation failed: %s", _e)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 