#!/usr/bin/env python3
import os
import json
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://raj:Rajshah11@localhost:5432/liquicity")
engine = create_engine(DATABASE_URL)

def update_user_currency():
    """
    Update the display currency for hadeermotair@gmail.com to EUR
    """
    email = "hadeermotair@gmail.com"
    
    # First, find the user ID
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, bridge_customer_id, country FROM users WHERE email = :email"),
            {"email": email}
        ).first()
        
        if not result:
            print(f"User with email {email} not found")
            return
        
        user_id, bridge_customer_id, country = result
        print(f"Found user with ID: {user_id}")
        print(f"Current country: {country}")
        
        # Check if wallet exists
        wallets = conn.execute(
            text("SELECT id, currency, local_currency FROM wallets WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).fetchall()
        
        if wallets:
            print(f"Found {len(wallets)} wallets:")
            for wallet in wallets:
                wallet_id, currency, local_currency = wallet
                print(f"Wallet ID: {wallet_id}, Currency: {currency}, Local Currency: {local_currency}")
                
                # Update wallet to use EUR as local currency
                conn.execute(
                    text("UPDATE wallets SET local_currency = 'eur', local_balance = balance WHERE id = :wallet_id"),
                    {"wallet_id": wallet_id}
                )
            
            # Also update the user's country to EU
            conn.execute(
                text("UPDATE users SET country = 'EU' WHERE id = :user_id"),
                {"user_id": user_id}
            )
            conn.commit()
            print(f"Updated all wallets to use EUR as local currency")
        else:
            print(f"No wallets found for this user. Make sure the user has completed the onboarding process.")
            
            # Update the user's country to EU
            conn.execute(
                text("UPDATE users SET country = 'EU' WHERE id = :user_id"),
                {"user_id": user_id}
            )
            conn.commit()
            print(f"Updated user's country to EU")
            
        print(f"Successfully updated currency settings for {email}")

if __name__ == "__main__":
    update_user_currency() 