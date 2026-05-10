-- =============================================================================
-- Full Database Migration Script
-- Generated from: /mnt/Extra/backend/app/models.py
-- Run this script on a fresh PostgreSQL database to build the entire schema.
-- =============================================================================

-- Drop tables in reverse dependency order (safe re-run)
DROP TABLE IF EXISTS saved_expenses    CASCADE;
DROP TABLE IF EXISTS savings           CASCADE;
DROP TABLE IF EXISTS transactions      CASCADE;
DROP TABLE IF EXISTS financial_summary CASCADE;
DROP TABLE IF EXISTS investment_profiles CASCADE;
DROP TABLE IF EXISTS goals             CASCADE;
DROP TABLE IF EXISTS users             CASCADE;

-- =============================================================================
-- 1. users
-- =============================================================================
CREATE TABLE users (
    id             SERIAL          PRIMARY KEY,
    email          VARCHAR(255)    NOT NULL UNIQUE,
    password       VARCHAR(255)    NOT NULL,
    name           VARCHAR(255),
    job_type       VARCHAR(100),
    monthly_salary FLOAT
);

CREATE INDEX idx_users_email ON users (email);

-- =============================================================================
-- 2. goals
-- (created before transactions because transactions has a FK to goals)
-- =============================================================================
CREATE TABLE goals (
    id             SERIAL          PRIMARY KEY,
    user_id        INTEGER         NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    title          VARCHAR(255)    NOT NULL,
    target_amount  FLOAT           NOT NULL,
    color          VARCHAR(50)     NOT NULL,
    category       VARCHAR(100)    NOT NULL DEFAULT 'Genel',
    icon           VARCHAR(100)    NOT NULL DEFAULT 'stars_rounded',
    is_completed   BOOLEAN         NOT NULL DEFAULT FALSE,
    completed_at   VARCHAR(50)
);

CREATE INDEX idx_goals_user_id ON goals (user_id);

-- =============================================================================
-- 3. transactions
-- =============================================================================
CREATE TABLE transactions (
    id           SERIAL          PRIMARY KEY,
    user_id      INTEGER         NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    goal_id      INTEGER                  REFERENCES goals (id)  ON DELETE SET NULL,
    amount       FLOAT           NOT NULL,
    description  VARCHAR(500)    NOT NULL,
    type         VARCHAR(10)     NOT NULL,   -- 'gelir' | 'gider'
    date         VARCHAR(20)     NOT NULL,
    category     VARCHAR(100)    NOT NULL DEFAULT 'Genel',
    is_recurring BOOLEAN         NOT NULL DEFAULT FALSE,
    currency     VARCHAR(10)     NOT NULL DEFAULT 'TRY',  -- 'TRY' | 'USD' | 'EUR' | 'GOLD'
    timestamp    TIMESTAMP                DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_user_id ON transactions (user_id);
CREATE INDEX idx_transactions_goal_id ON transactions (goal_id);

-- =============================================================================
-- 4. financial_summary
-- =============================================================================
CREATE TABLE financial_summary (
    id               SERIAL          PRIMARY KEY,
    user_id          INTEGER         NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    month            VARCHAR(20)     NOT NULL DEFAULT 'Ocak',
    monthly_income   FLOAT           NOT NULL DEFAULT 0.0,
    monthly_expense  FLOAT           NOT NULL DEFAULT 0.0,
    monthly_savings  FLOAT           NOT NULL DEFAULT 0.0
);

CREATE INDEX idx_financial_summary_user_id ON financial_summary (user_id);

-- =============================================================================
-- 5. investment_profiles
-- =============================================================================
CREATE TABLE investment_profiles (
    id       SERIAL          PRIMARY KEY,
    user_id  INTEGER         NOT NULL UNIQUE REFERENCES users (id) ON DELETE CASCADE,
    profile  VARCHAR(50)     NOT NULL   -- 'korumacı' | 'dengeli' | 'agresif'
);

CREATE INDEX idx_investment_profiles_user_id ON investment_profiles (user_id);

-- =============================================================================
-- 6. savings
-- =============================================================================
CREATE TABLE savings (
    id          SERIAL          PRIMARY KEY,
    user_id     INTEGER         NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    amount      FLOAT           NOT NULL,
    currency    VARCHAR(10)     NOT NULL,   -- 'TRY' | 'USD' | 'EUR' | 'GOLD'
    description TEXT,
    date        VARCHAR(20)     NOT NULL,
    timestamp   TIMESTAMP                DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_savings_user_id ON savings (user_id);

-- =============================================================================
-- 7. saved_expenses
-- =============================================================================
CREATE TABLE saved_expenses (
    id       SERIAL          PRIMARY KEY,
    user_id  INTEGER         NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    label    VARCHAR(255)    NOT NULL,
    amount   FLOAT           NOT NULL,
    category VARCHAR(100)    NOT NULL DEFAULT 'Genel'
);

CREATE INDEX idx_saved_expenses_user_id ON saved_expenses (user_id);

-- =============================================================================
-- End of migration
-- =============================================================================
