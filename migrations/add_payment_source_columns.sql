-- Migration to add payment_source and transaction_type columns to transactions table

-- Check if columns already exist before adding them
DO $$
BEGIN
    -- Add payment_source column if it doesn't exist
    IF NOT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_name = 'transactions' AND column_name = 'payment_source'
    ) THEN
        ALTER TABLE transactions ADD COLUMN payment_source VARCHAR(50);
    END IF;

    -- Add transaction_type column if it doesn't exist
    IF NOT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_name = 'transactions' AND column_name = 'transaction_type'
    ) THEN
        ALTER TABLE transactions ADD COLUMN transaction_type VARCHAR(50) DEFAULT 'TRANSFER';
    END IF;
END
$$; 