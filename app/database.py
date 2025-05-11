import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Load environment variables from .env file if present
load_dotenv()

# DATABASE_URL is now loaded from an environment variable for better security.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://raj:Rajshah11@localhost:5432/liquicity")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Ensure basic supplemental tables exist if Alembic not used yet
with engine.connect() as conn:
    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS notifications (
        id SERIAL PRIMARY KEY,
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        type VARCHAR(20) NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT now()
    );
    CREATE TABLE IF NOT EXISTS money_requests (
        id SERIAL PRIMARY KEY,
        requester_id UUID REFERENCES users(id) ON DELETE CASCADE,
        amount NUMERIC(18,2) NOT NULL,
        note TEXT,
        status VARCHAR(20) DEFAULT 'pending', -- pending, paid, cancelled
        created_at TIMESTAMP DEFAULT now()
    );
    CREATE TABLE IF NOT EXISTS card_accounts (
        id SERIAL PRIMARY KEY,
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        bridge_card_id VARCHAR(64) UNIQUE,
        last4 VARCHAR(4),
        state VARCHAR(20),
        created_at TIMESTAMP DEFAULT now()
    );
    """))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
