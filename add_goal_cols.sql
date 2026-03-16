-- Add is_completed to goals table
ALTER TABLE goals ADD COLUMN is_completed INTEGER DEFAULT 0;

-- Drop unique constraint on user_id in goals table map to allow multiple goals
-- This typically includes identifying the constraint name; commonly it's goals_user_id_key
ALTER TABLE goals DROP CONSTRAINT IF EXISTS goals_user_id_key;

-- Add goal_id to transactions table
ALTER TABLE transactions ADD COLUMN goal_id INTEGER REFERENCES goals (id) ON DELETE SET NULL;
