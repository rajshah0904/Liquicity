#!/usr/bin/env python
import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import bcrypt
from dotenv import load_dotenv

load_dotenv()

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
    
    # Clean existing lean tables to ensure correct schema
    cursor.execute("DROP TABLE IF EXISTS wallet_transactions CASCADE")
    cursor.execute("DROP TABLE IF EXISTS wallets CASCADE")
    cursor.execute("DROP TABLE IF EXISTS transfers CASCADE")
    cursor.execute("DROP TABLE IF EXISTS card_accounts CASCADE")
    cursor.execute("DROP TABLE IF EXISTS external_accounts CASCADE")
    cursor.execute("DROP TABLE IF EXISTS kyc_submissions CASCADE")
    cursor.execute("DROP TABLE IF EXISTS users CASCADE")
    cursor.execute("DROP TABLE IF EXISTS bank_accounts CASCADE")
    cursor.execute("DROP TABLE IF EXISTS transactions CASCADE")
    cursor.execute("DROP TABLE IF EXISTS teams CASCADE")
    cursor.execute("DROP TABLE IF EXISTS team_members CASCADE")

    # Create tables
    print("Creating tables (lean Bridge schema)...")

    # Enable pgcrypto for UUID generation
    cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # --------------------
    # 1. USERS
    # --------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        auth0_user_id TEXT UNIQUE NOT NULL,
        email TEXT NOT NULL,
        name TEXT,
        country CHAR(2) NOT NULL,
        bridge_customer_id TEXT UNIQUE,
        kyc_status TEXT,
        account_type TEXT DEFAULT 'auth0',
        wallet_address TEXT,
        first_name TEXT,
        last_name TEXT,
        is_verified BOOLEAN DEFAULT FALSE,
        role TEXT DEFAULT 'user',
        is_active BOOLEAN DEFAULT TRUE,
        auth0_id TEXT UNIQUE,
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now()
    )
    """)

    # --------------------
    # 2. KYC SUBMISSIONS (raw staged data)
    # --------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kyc_submissions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id),
        payload JSONB NOT NULL,
        status TEXT DEFAULT 'pending',
        error_msg TEXT,
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now()
    )
    """)

    # --------------------
    # 3. EXTERNAL ACCOUNTS (bank rails)
    # --------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS external_accounts (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id),
        external_account_id TEXT UNIQUE NOT NULL,
        activation_method TEXT NOT NULL,     -- 'plaid' | 'raw'
        payment_rail TEXT NOT NULL,          -- 'ach' | 'sepa' | 'spei'
        currency TEXT NOT NULL,              -- 'usd' | 'eur' | 'mxn'
        details JSONB NOT NULL,
        active BOOLEAN DEFAULT true,
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now()
    )
    """)

    # --------------------
    # 4. CARD ACCOUNTS (Bridge Visa)
    # --------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS card_accounts (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id),
        card_account_id TEXT UNIQUE NOT NULL,
        client_reference_id TEXT,
        currency TEXT NOT NULL,
        chain TEXT NOT NULL,
        last_4 TEXT,
        expiry TEXT,
        status TEXT,
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now()
    )
    """)

    # --------------------
    # 5. TRANSFERS (prefunded audit log)
    # --------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transfers (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id),
        transfer_id TEXT UNIQUE NOT NULL,
        amount NUMERIC NOT NULL,
        src_rail TEXT NOT NULL,              -- 'prefunded'
        dst_rail TEXT NOT NULL,              -- 'ach' | 'sepa' | 'spei' | 'card'
        currency_src TEXT NOT NULL,
        currency_dst TEXT NOT NULL,
        state TEXT NOT NULL,
        receipt JSONB,
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now()
    )
    """)

    # --------------------
    # 6. WALLETS (cached balances)
    # --------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wallets (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id),
        bridge_wallet_id TEXT UNIQUE NOT NULL,
        currency TEXT NOT NULL,
        balance NUMERIC NOT NULL,
        local_currency TEXT NOT NULL,
        local_balance NUMERIC NOT NULL,
        last_fetched_at TIMESTAMPTZ,
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now()
    )
    """)

    # --------------------
    # 7. WALLET TRANSACTIONS
    # --------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wallet_transactions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        wallet_id UUID REFERENCES wallets(id),
        transaction_id TEXT UNIQUE NOT NULL,
        amount NUMERIC NOT NULL,
        currency TEXT NOT NULL,
        description TEXT,
        date DATE,
        booking_date DATE,
        transaction_date DATE,
        value_date DATE,
        updated_at TIMESTAMPTZ,
        created_at TIMESTAMPTZ DEFAULT now()
    )
    """)

    # ---- INDEXES ----
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_auth0_id ON users(auth0_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_external_accounts_user ON external_accounts(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_card_accounts_user ON card_accounts(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_wallets_user ON wallets(user_id)")

    print("✅ Lean tables created (or already existed)")

    # Commit changes
    conn.commit()

    # Close connection
    cursor.close()
    conn.close()

    print("\n✅ Database setup complete! (Lean schema)")
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