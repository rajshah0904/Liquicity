import os
import sys
import psycopg2
import bcrypt
from datetime import datetime

# Database connection
db_url = "postgresql://raj:Rajshah11@localhost:5432/terraflow"

try:
    print("Connecting to database...")
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Drop and recreate tables
    print("Dropping existing tables...")
    cursor.execute("DROP TABLE IF EXISTS transactions CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS wallets CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS users CASCADE;")
    
    # Create tables
    print("Creating users table...")
    cursor.execute("""
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR UNIQUE NOT NULL,
        hashed_password VARCHAR NOT NULL,
        wallet_address VARCHAR,
        email VARCHAR UNIQUE,
        role VARCHAR DEFAULT 'user',
        created_at TIMESTAMP DEFAULT NOW(),
        is_active BOOLEAN DEFAULT TRUE,
        first_name VARCHAR,
        last_name VARCHAR,
        date_of_birth VARCHAR,
        country VARCHAR,
        nationality VARCHAR,
        gender VARCHAR,
        ssn VARCHAR,
        street_address VARCHAR,
        street_address_2 VARCHAR,
        city VARCHAR,
        state VARCHAR,
        postal_code VARCHAR,
        address_country VARCHAR,
        stripe_customer_id VARCHAR
    );
    """)
    
    print("Creating wallets table...")
    cursor.execute("""
    CREATE TABLE wallets (
        id SERIAL PRIMARY KEY,
        user_id INTEGER UNIQUE REFERENCES users(id),
        fiat_balance FLOAT DEFAULT 0.0,
        stablecoin_balance FLOAT DEFAULT 0.0,
        base_currency VARCHAR DEFAULT 'USD',
        display_currency VARCHAR DEFAULT 'USD',
        country_code VARCHAR,
        blockchain_address VARCHAR,
        currency_settings JSON
    );
    """)
    
    print("Creating transactions table...")
    cursor.execute("""
    CREATE TABLE transactions (
        id SERIAL PRIMARY KEY,
        sender_id INTEGER REFERENCES users(id),
        recipient_id INTEGER REFERENCES users(id),
        stablecoin_amount FLOAT NOT NULL,
        source_amount FLOAT NOT NULL,
        source_currency VARCHAR NOT NULL,
        target_amount FLOAT NOT NULL,
        target_currency VARCHAR NOT NULL,
        source_to_stablecoin_rate FLOAT NOT NULL,
        stablecoin_to_target_rate FLOAT NOT NULL,
        timestamp TIMESTAMP DEFAULT NOW(),
        status VARCHAR DEFAULT 'pending',
        blockchain_txn_hash VARCHAR
    );
    """)
    
    # Create a test user
    print("Creating test user...")
    
    # Hash the password
    password = "test123"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Insert user
    cursor.execute("""
    INSERT INTO users (username, email, hashed_password, first_name, last_name, role)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING id;
    """, ("testuser", "test@example.com", hashed_password, "Test", "User", "admin"))
    
    user_id = cursor.fetchone()[0]
    
    # Create a wallet for the test user
    cursor.execute("""
    INSERT INTO wallets (user_id, fiat_balance, stablecoin_balance, base_currency, display_currency, country_code, blockchain_address)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """, (user_id, 10000.0, 5000.0, "USD", "USD", "US", "0x1234567890abcdef1234567890abcdef12345678"))
    
    # Commit the transaction
    conn.commit()
    
    print(f"Test user created with ID: {user_id}")
    print(f"Username: testuser")
    print(f"Password: test123")
    print(f"Initial balance: $10,000 USD and 5,000 USDT")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close() 