import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, Wallet
import bcrypt

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://raj:Rajshah11@localhost:5432/terraflow")
engine = create_engine(DATABASE_URL)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Create a second test user with minimal information
    print("Creating second test user...")
    
    # Hash the password
    password = "test456"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create user
    test_user = User(
        username="testuser2",
        email="test2@example.com",
        hashed_password=hashed_password,
        first_name="Test",
        last_name="User2",
        role="user"  # Regular user role
    )
    
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    # Create a wallet for the test user
    wallet = Wallet(
        user_id=test_user.id,
        fiat_balance=5000.0,  # $5,000 for testing
        stablecoin_balance=2000.0,  # 2,000 USDT
        base_currency="USD",
        display_currency="USD",
        country_code="US",
        blockchain_address="0x0987654321fedcba0987654321fedcba09876543"
    )
    
    db.add(wallet)
    db.commit()
    
    print(f"Second test user created with ID: {test_user.id}")
    print(f"Username: testuser2")
    print(f"Password: test456")
    print(f"Initial balance: $5,000 USD and 2,000 USDT")
    
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close() 