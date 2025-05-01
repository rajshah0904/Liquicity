import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Use hardcoded database URL since environment variable is not set
database_url = "postgresql://raj:Rajshah11@localhost:5432/liquicity"
print(f"Using database URL: {database_url}")

# Create engine and session
try:
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # First, let's check the columns in the wallets table
    columns_result = session.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'wallets'
    """)).fetchall()
    
    print("Columns in wallets table:")
    for col in columns_result:
        print(f"  - {col[0]}")
    
    # Get user ID for testuser2
    user_result = session.execute(text("SELECT id FROM users WHERE username = 'testuser2'")).first()
    
    if not user_result:
        print("User testuser2 not found")
        sys.exit(1)
    
    user_id = user_result[0]
    print(f"Found testuser2 with ID: {user_id}")
    
    # Query wallet for testuser2 with explicit columns
    wallet_result = session.execute(
        text("""
            SELECT id, user_id, fiat_balance, stablecoin_balance, base_currency 
            FROM wallets 
            WHERE user_id = :user_id
        """),
        {"user_id": user_id}
    ).first()
    
    if not wallet_result:
        print(f"No wallet found for testuser2 (ID: {user_id})")
        sys.exit(1)
    
    print(f"\nWallet information for testuser2 (ID: {user_id}):")
    print(f"Wallet ID: {wallet_result[0]}")
    print(f"User ID: {wallet_result[1]}")
    print(f"Fiat Balance: ${wallet_result[2]:.2f}")
    print(f"Stablecoin Balance: {wallet_result[3]:.2f} USDT")
    print(f"Base Currency: {wallet_result[4] or 'USD'}")
    
    session.close()
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1) 