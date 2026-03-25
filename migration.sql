-- Migration script to recreate savings table
CREATE TABLE IF NOT EXISTS savings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount FLOAT NOT NULL,
    currency VARCHAR(10) NOT NULL,
    description TEXT,
    date VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_savings_user_id ON savings(user_id);
