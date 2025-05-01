from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def add_google_auth_columns():
    """Add Google OAuth related columns and modify existing ones."""
    try:
        with SessionLocal() as session:
            # Make username and hashed_password nullable
            session.execute(text("""
                ALTER TABLE users 
                ALTER COLUMN hashed_password DROP NOT NULL
            """))
            
            # Add Google OAuth related columns
            session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS google_id VARCHAR UNIQUE,
                ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS verification_token VARCHAR,
                ADD COLUMN IF NOT EXISTS verification_token_expires_at TIMESTAMP
            """))
            
            # Update existing users to have email_verified = true
            session.execute(text("""
                UPDATE users 
                SET email_verified = TRUE 
                WHERE email_verified IS NULL
            """))
            
            session.commit()
            print("Successfully added Google OAuth columns and modified existing ones")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        session.rollback()
        raise

if __name__ == "__main__":
    add_google_auth_columns() 