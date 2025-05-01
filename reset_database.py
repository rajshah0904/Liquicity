import os
import psycopg2
import bcrypt
import json
from datetime import datetime, timezone

# Database connection
db_url = "postgresql://raj:Rajshah11@localhost:5432/liquicity"

try:
    print("Connecting to database...")
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Drop all relevant tables in the correct order (respecting foreign key constraints)
    print("Dropping existing tables...")
    tables = [
        "transactions", "wallets", "blockchain_transactions", "blockchain_wallets",
        "bank_accounts", "ai_messages", "ai_conversations", "ai_actions", "ai_agents",
        "data_pipeline_runs", "data_pipelines", "data_queries", "user_metadata",
        "team_members", "teams", "trades", "users"
    ]
    
    for table in tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
            print(f"- Dropped table {table}")
        except Exception as e:
            print(f"- Error dropping {table}: {str(e)}")
    
    # Create tables with all required signup fields
    print("\nCreating users table...")
    cursor.execute("""
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR UNIQUE NOT NULL,
        hashed_password VARCHAR NOT NULL,
        wallet_address VARCHAR,
        email VARCHAR UNIQUE NOT NULL,
        role VARCHAR DEFAULT 'user',
        created_at TIMESTAMP DEFAULT NOW(),
        is_active BOOLEAN DEFAULT TRUE,
        -- Personal information
        first_name VARCHAR,
        last_name VARCHAR,
        date_of_birth VARCHAR,
        country VARCHAR,
        nationality VARCHAR,
        gender VARCHAR,
        ssn VARCHAR,
        -- Address information
        street_address VARCHAR,
        street_address_2 VARCHAR,
        city VARCHAR,
        state VARCHAR,
        postal_code VARCHAR,
        address_country VARCHAR,
        -- Stripe info
        stripe_customer_id VARCHAR
    );
    """)
    
    print("Creating teams table...")
    cursor.execute("""
    CREATE TABLE teams (
        id SERIAL PRIMARY KEY,
        name VARCHAR UNIQUE NOT NULL,
        description VARCHAR,
        created_at TIMESTAMP DEFAULT NOW(),
        owner_id INTEGER REFERENCES users(id)
    );
    """)
    
    print("Creating team_members join table...")
    cursor.execute("""
    CREATE TABLE team_members (
        user_id INTEGER REFERENCES users(id),
        team_id INTEGER REFERENCES teams(id),
        PRIMARY KEY (user_id, team_id)
    );
    """)
    
    print("Creating user_metadata table...")
    cursor.execute("""
    CREATE TABLE user_metadata (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) UNIQUE,
        first_name VARCHAR,
        last_name VARCHAR,
        date_of_birth VARCHAR,
        country VARCHAR,
        country_code VARCHAR,
        id_number VARCHAR, 
        id_type VARCHAR,
        document_type VARCHAR,
        document_number VARCHAR,
        address_street VARCHAR,
        address_city VARCHAR,
        address_state VARCHAR,
        address_postal VARCHAR,
        phone_number VARCHAR,
        verification_status VARCHAR DEFAULT 'unverified',
        verified_at TIMESTAMP,
        profile_data JSONB,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    """)
    
    print("Creating wallets table...")
    cursor.execute("""
    CREATE TABLE wallets (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) UNIQUE,
        fiat_balance FLOAT DEFAULT 0.0,
        stablecoin_balance FLOAT DEFAULT 0.0,
        base_currency VARCHAR DEFAULT 'USD',
        display_currency VARCHAR DEFAULT 'USD',
        country_code VARCHAR,
        blockchain_address VARCHAR,
        currency_settings JSONB
    );
    """)
    
    print("Creating trades table...")
    cursor.execute("""
    CREATE TABLE trades (
        id SERIAL PRIMARY KEY,
        sender_id INTEGER REFERENCES users(id),
        recipient_id INTEGER REFERENCES users(id),
        stablecoin_amount FLOAT NOT NULL,
        fiat_amount FLOAT NOT NULL,
        conversion_rate FLOAT NOT NULL,
        timestamp TIMESTAMP DEFAULT NOW(),
        status VARCHAR DEFAULT 'pending'
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
    
    print("Creating blockchain_wallets table...")
    cursor.execute("""
    CREATE TABLE blockchain_wallets (
        id SERIAL PRIMARY KEY,
        address VARCHAR NOT NULL,
        chain VARCHAR NOT NULL,
        wallet_type VARCHAR NOT NULL,
        name VARCHAR NOT NULL,
        user_id INTEGER REFERENCES users(id),
        team_id INTEGER REFERENCES teams(id),
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT NOW(),
        safe_address VARCHAR,
        safe_owners JSONB,
        safe_threshold INTEGER,
        meta_data JSONB,
        private_key_encrypted VARCHAR
    );
    """)
    
    print("Creating blockchain_transactions table...")
    cursor.execute("""
    CREATE TABLE blockchain_transactions (
        id SERIAL PRIMARY KEY,
        txn_hash VARCHAR NOT NULL,
        chain VARCHAR NOT NULL,
        from_address VARCHAR NOT NULL,
        to_address VARCHAR NOT NULL,
        value VARCHAR NOT NULL,
        gas_price VARCHAR,
        gas_used VARCHAR,
        status VARCHAR DEFAULT 'pending',
        block_number INTEGER,
        timestamp TIMESTAMP DEFAULT NOW(),
        function_name VARCHAR,
        function_args JSONB,
        wallet_id INTEGER REFERENCES blockchain_wallets(id),
        meta_data JSONB
    );
    """)
    
    print("Creating bank_accounts table...")
    cursor.execute("""
    CREATE TABLE bank_accounts (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        stripe_bank_id VARCHAR UNIQUE,
        bank_name VARCHAR,
        account_type VARCHAR,
        last4 VARCHAR,
        country VARCHAR,
        currency VARCHAR,
        status VARCHAR DEFAULT 'active',
        created_at TIMESTAMP DEFAULT NOW(),
        last_updated TIMESTAMP DEFAULT NOW(),
        bank_metadata TEXT
    );
    """)
    
    # Create additional tables for AI and data features
    print("Creating ai_agents table...")
    cursor.execute("""
    CREATE TABLE ai_agents (
        id SERIAL PRIMARY KEY,
        name VARCHAR NOT NULL,
        description TEXT,
        agent_type VARCHAR NOT NULL,
        model VARCHAR NOT NULL,
        created_at TIMESTAMP DEFAULT NOW(),
        is_active BOOLEAN DEFAULT TRUE,
        configuration JSONB
    );
    """)
    
    print("Creating ai_conversations table...")
    cursor.execute("""
    CREATE TABLE ai_conversations (
        id SERIAL PRIMARY KEY,
        agent_id INTEGER REFERENCES ai_agents(id),
        user_id INTEGER,
        started_at TIMESTAMP DEFAULT NOW(),
        last_message_at TIMESTAMP DEFAULT NOW(),
        channel VARCHAR NOT NULL,
        meta_data JSONB
    );
    """)
    
    print("Creating ai_messages table...")
    cursor.execute("""
    CREATE TABLE ai_messages (
        id SERIAL PRIMARY KEY,
        conversation_id INTEGER REFERENCES ai_conversations(id),
        role VARCHAR NOT NULL,
        content TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT NOW()
    );
    """)
    
    print("Creating ai_actions table...")
    cursor.execute("""
    CREATE TABLE ai_actions (
        id SERIAL PRIMARY KEY,
        agent_id INTEGER REFERENCES ai_agents(id),
        conversation_id INTEGER REFERENCES ai_conversations(id),
        action_type VARCHAR NOT NULL,
        status VARCHAR DEFAULT 'pending',
        input_data JSONB,
        output_data JSONB,
        started_at TIMESTAMP DEFAULT NOW(),
        completed_at TIMESTAMP,
        error_message TEXT
    );
    """)
    
    print("Creating data_queries table...")
    cursor.execute("""
    CREATE TABLE data_queries (
        id SERIAL PRIMARY KEY,
        natural_language_query TEXT NOT NULL,
        generated_query TEXT NOT NULL,
        query_type VARCHAR NOT NULL,
        created_by_id INTEGER REFERENCES users(id),
        created_at TIMESTAMP DEFAULT NOW(),
        execution_time_ms INTEGER,
        result_summary TEXT,
        is_saved BOOLEAN DEFAULT FALSE
    );
    """)
    
    print("Creating data_pipelines table...")
    cursor.execute("""
    CREATE TABLE data_pipelines (
        id SERIAL PRIMARY KEY,
        name VARCHAR NOT NULL,
        description TEXT,
        natural_language_definition TEXT NOT NULL,
        generated_code TEXT NOT NULL,
        schedule VARCHAR,
        last_run TIMESTAMP,
        created_at TIMESTAMP DEFAULT NOW(),
        is_active BOOLEAN DEFAULT TRUE
    );
    """)
    
    print("Creating data_pipeline_runs table...")
    cursor.execute("""
    CREATE TABLE data_pipeline_runs (
        id SERIAL PRIMARY KEY,
        pipeline_id INTEGER REFERENCES data_pipelines(id),
        started_at TIMESTAMP DEFAULT NOW(),
        completed_at TIMESTAMP,
        status VARCHAR DEFAULT 'running',
        log_output TEXT,
        error_message TEXT
    );
    """)
    
    conn.commit()
    print("\nDatabase schema created successfully!")
    
    # Create a test user with complete profile data
    print("\nCreating test user...")
    
    # Hash the password - test123
    password = "test123"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Insert user with all required fields
    cursor.execute("""
    INSERT INTO users (
        username, email, hashed_password, role, first_name, last_name, 
        date_of_birth, country, nationality, gender, ssn, 
        street_address, city, state, postal_code, address_country
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id;
    """, (
        "testuser", "test@example.com", hashed_password, "admin", 
        "Test", "User", "1990-01-01", "United States", "American", "Male", "123-45-6789",
        "123 Main St", "San Francisco", "CA", "94105", "United States"
    ))
    
    user_id = cursor.fetchone()[0]
    
    # Create a wallet for the test user
    cursor.execute("""
    INSERT INTO wallets (
        user_id, fiat_balance, stablecoin_balance, base_currency, 
        display_currency, country_code, blockchain_address
    ) VALUES (%s, %s, %s, %s, %s, %s, %s);
    """, (
        user_id, 10000.0, 5000.0, "USD", "USD", "US", 
        "0x1234567890abcdef1234567890abcdef12345678"
    ))
    
    # Create user metadata for the test user
    cursor.execute("""
    INSERT INTO user_metadata (
        user_id, first_name, last_name, date_of_birth, country, country_code,
        id_number, id_type, document_type, document_number, address_street,
        address_city, address_state, address_postal, phone_number,
        verification_status, profile_data
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """, (
        user_id, "Test", "User", "1990-01-01", "United States", "US",
        "123-45-6789", "SSN", "Passport", "US123456789", "123 Main St",
        "San Francisco", "CA", "94105", "+1-555-123-4567",
        "verified", json.dumps({
            "occupation": "Software Engineer",
            "employer": "Liquicity Inc.",
            "income_range": "$100,000 - $150,000",
            "preferred_language": "English",
            "notification_preferences": {
                "email": True,
                "sms": True,
                "push": True
            }
        })
    ))
    
    # Create a bank account for the test user
    cursor.execute("""
    INSERT INTO bank_accounts (
        user_id, stripe_bank_id, bank_name, account_type, last4,
        country, currency, status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """, (
        user_id, "ba_test123456789", "Chase Bank", "checking", "6789",
        "US", "USD", "active"
    ))
    
    # Commit the transaction
    conn.commit()
    
    print(f"\nTest user created with ID: {user_id}")
    print(f"Username: testuser")
    print(f"Password: test123")
    print(f"Initial balance: $10,000 USD and 5,000 USDT")
    print("User has complete profile data for testing all features")
    
except Exception as e:
    print(f"\nError: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()
    print("\nDatabase connection closed.") 