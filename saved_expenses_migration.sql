-- Migration: Add saved_expenses table for Quick-Add expense templates
-- Date: 2026-03-31
-- Run against the GençCüzdan database

-- 1. Create the saved_expenses table
CREATE TABLE IF NOT EXISTS saved_expenses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    label VARCHAR NOT NULL,
    amount FLOAT NOT NULL,
    category VARCHAR NOT NULL DEFAULT 'Genel'
);

CREATE INDEX IF NOT EXISTS ix_saved_expenses_id ON saved_expenses(id);
CREATE INDEX IF NOT EXISTS ix_saved_expenses_user_id ON saved_expenses(user_id);
