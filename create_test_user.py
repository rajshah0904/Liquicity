import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, Wallet
from app.database import get_db
import bcrypt

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://raj:Rajshah11@localhost:5432/liquicity")
engine = create_engine(DATABASE_URL)

# Drop all tables and recreate them
print("Recreating database tables...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Create a test user with minimal information
    print("Creating test user...")
    
    # Hash the password
    password = "test123"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create user
    test_user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hashed_password,
        first_name="Test",
        last_name="User",
        role="admin"  # Admin for full access
    )
    
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    # Create a wallet for the test user
    wallet = Wallet(
        user_id=test_user.id,
        fiat_balance=10000.0,  # $10,000 for testing
        stablecoin_balance=5000.0,  # 5,000 USDT
        base_currency="USD",
        display_currency="USD",
        country_code="US",
        blockchain_address="0x1234567890abcdef1234567890abcdef12345678"
    )
    
    db.add(wallet)
    db.commit()
    
    print(f"Test user created with ID: {test_user.id}")
    print(f"Username: testuser")
    print(f"Password: test123")
    print(f"Initial balance: $10,000 USD and 5,000 USDT")
    
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close() 