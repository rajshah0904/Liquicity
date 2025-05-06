-- Migration to remove blockchain and stablecoin-related fields
-- This script removes the stablecoin_balance and blockchain_address columns from the wallets table

-- First back up the wallets table structure
CREATE TABLE wallets_backup AS SELECT id, user_id, fiat_balance, base_currency, display_currency, country_code, currency_settings FROM wallets;

-- Drop the original table
DROP TABLE wallets;

-- Recreate the table without the removed columns
CREATE TABLE wallets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) UNIQUE,
    fiat_balance FLOAT DEFAULT 0.0,
    base_currency VARCHAR DEFAULT 'USD',
    display_currency VARCHAR DEFAULT 'USD',
    country_code VARCHAR,
    currency_settings JSON
);

-- Copy data back from the backup
INSERT INTO wallets (id, user_id, fiat_balance, base_currency, display_currency, country_code, currency_settings)
SELECT id, user_id, fiat_balance, base_currency, display_currency, country_code, currency_settings FROM wallets_backup;

-- Drop the backup table
DROP TABLE wallets_backup;

-- Update sequences
SELECT setval('wallets_id_seq', (SELECT MAX(id) FROM wallets), true);

-- Drop blockchain-related tables if they exist
DROP TABLE IF EXISTS blockchain_transactions;
DROP TABLE IF EXISTS blockchain_wallets;

-- Drop AI-related tables if they exist
DROP TABLE IF EXISTS ai_messages;
DROP TABLE IF EXISTS ai_actions;
DROP TABLE IF EXISTS ai_conversations;
DROP TABLE IF EXISTS ai_agents;

-- Drop data analytics tables if they exist
DROP TABLE IF EXISTS data_pipeline_runs;
DROP TABLE IF EXISTS data_pipelines;
DROP TABLE IF EXISTS data_queries; 