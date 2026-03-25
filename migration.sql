-- Migration script to refactor savings into transactions table
-- Add currency column to transactions
ALTER TABLE transactions ADD COLUMN currency VARCHAR(10) DEFAULT 'TRY';

-- Drop savings table if it exists (from previous implementation attempt)
DROP TABLE IF EXISTS savings;
