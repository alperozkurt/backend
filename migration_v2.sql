-- migration_v2.sql
-- Adds the is_need boolean column to the transactions table for tracking Needs vs Wants.

ALTER TABLE transactions ADD COLUMN IF NOT EXISTS is_need BOOLEAN DEFAULT TRUE;
