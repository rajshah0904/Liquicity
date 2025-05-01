#!/usr/bin/env python
import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import bcrypt

print("Liquicity PostgreSQL Setup Script")
print("=================================")

# Default credentials
DEFAULT_USER = "raj"
DEFAULT_PASSWORD = "Rajshah11"
DEFAULT_DB = "liquicity"

# Step 1: Check if PostgreSQL is installed
try:
    subprocess.run(["psql", "--version"], check=True, capture_output=True)
    print("✅ PostgreSQL is installed")
except (subprocess.CalledProcessError, FileNotFoundError):
    print("❌ PostgreSQL is not installed or not in PATH")
    print("Please install PostgreSQL and try again")
    sys.exit(1)

# Step 2: Connect to PostgreSQL and create database
try:
    # Connect to default postgres database
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        host="localhost"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Create user if not exists
    cursor.execute(f"SELECT 1 FROM pg_roles WHERE rolname='{DEFAULT_USER}'")
    if not cursor.fetchone():
        print(f"Creating user '{DEFAULT_USER}'...")
        cursor.execute(f"CREATE USER {DEFAULT_USER} WITH PASSWORD '{DEFAULT_PASSWORD}'")
    else:
        print(f"User '{DEFAULT_USER}' already exists")
    
    # Create database if not exists
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{DEFAULT_DB}'")
    if not cursor.fetchone():
        print(f"Creating database '{DEFAULT_DB}'...")
        cursor.execute(f"CREATE DATABASE {DEFAULT_DB} OWNER {DEFAULT_USER}")
    else:
        print(f"Database '{DEFAULT_DB}' already exists")
    
    # Grant privileges
    cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {DEFAULT_DB} TO {DEFAULT_USER}")
    
    # Close connection
    cursor.close()
    conn.close()
    print("✅ Database setup complete")
    
except Exception as e:
    print(f"❌ Error during database setup: {e}")
    sys.exit(1)

# Step 3: Create tables and test user
try:
    # Connect to our database
    print("Connecting to Liquicity database...")
    conn = psycopg2.connect(
        dbname=DEFAULT_DB,
        user=DEFAULT_USER,
        password=DEFAULT_PASSWORD,
        host="localhost"
    )
    cursor = conn.cursor()
    
    # Create tables
    print("Creating tables...")
    
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
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
    )
    """)
    
    # Create wallets table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wallets (
        id SERIAL PRIMARY KEY,
        user_id INTEGER UNIQUE REFERENCES users(id),
        fiat_balance FLOAT DEFAULT 0.0,
        stablecoin_balance FLOAT DEFAULT 0.0,
        base_currency VARCHAR DEFAULT 'USD',
        display_currency VARCHAR DEFAULT 'USD',
        country_code VARCHAR,
        blockchain_address VARCHAR,
        currency_settings JSON
    )
    """)
    
    # Create transactions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id SERIAL PRIMARY KEY,
        sender_id INTEGER REFERENCES users(id),
        recipient_id INTEGER REFERENCES users(id),
        amount FLOAT NOT NULL,
        currency VARCHAR NOT NULL,
        transaction_type VARCHAR NOT NULL,
        status VARCHAR NOT NULL,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        description VARCHAR,
        transaction_id VARCHAR,
        external_transaction_id VARCHAR,
        blockchain_transaction_hash VARCHAR,
        fees FLOAT DEFAULT 0.0,
        meta_data JSON
    )
    """)
    
    # Create blockchain_wallets table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blockchain_wallets (
        id SERIAL PRIMARY KEY,
        address VARCHAR NOT NULL,
        chain VARCHAR NOT NULL,
        wallet_type VARCHAR NOT NULL,
        name VARCHAR,
        user_id INTEGER REFERENCES users(id),
        team_id INTEGER,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT NOW(),
        safe_address VARCHAR,
        safe_owners VARCHAR[],
        safe_threshold INTEGER,
        meta_data JSON,
        private_key_encrypted VARCHAR
    )
    """)
    
    # Check if test user exists
    cursor.execute("SELECT id FROM users WHERE username = 'testuser'")
    if not cursor.fetchone():
        # Create test user
        print("Creating test user...")
        password = "test123"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute("""
        INSERT INTO users (username, email, hashed_password, first_name, last_name, role)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """, ('testuser', 'test@example.com', hashed_password, 'Test', 'User', 'admin'))
        
        user_id = cursor.fetchone()[0]
        
        # Create wallet for test user
        cursor.execute("""
        INSERT INTO wallets (user_id, fiat_balance, stablecoin_balance, base_currency, display_currency, country_code, blockchain_address)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, 10000.0, 5000.0, 'USD', 'USD', 'US', '0x1234567890abcdef1234567890abcdef12345678'))
        
        print(f"✅ Test user created with ID: {user_id}")
        print("   Username: testuser")
        print("   Password: test123")
        print("   Role: admin")
        print("   Initial balance: $10,000 USD and 5,000 USDT")
    else:
        print("✅ Test user already exists")
    
    # Commit changes
    conn.commit()
    
    # Close connection
    cursor.close()
    conn.close()
    
    print("\n✅ Database setup complete!")
    print("\nYou can now start the application with:")
    print("   - Backend: python -m app.main")
    print("   - Frontend: cd frontend && npm start")
    
except Exception as e:
    print(f"❌ Error during table setup: {e}")
    if 'conn' in locals() and conn is not None:
        conn.rollback()
    sys.exit(1)

# Create or update .env file
try:
    print("\nUpdating .env file...")
    with open('.env', 'w') as f:
        f.write(f"DATABASE_URL=postgresql://{DEFAULT_USER}:{DEFAULT_PASSWORD}@localhost:5432/{DEFAULT_DB}\n")
        f.write("APP_URL=http://localhost:3000\n")
    print("✅ .env file updated")
except Exception as e:
    print(f"❌ Error updating .env file: {e}")

print("\n🎉 Setup completed successfully! Your collaborator should now be able to run the application.") 