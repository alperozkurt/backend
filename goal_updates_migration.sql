-- PostgreSQL Migration for Goal Improvements

-- Add icon field (default to a generic icon)
ALTER TABLE goals 
ADD COLUMN IF NOT EXISTS icon VARCHAR NOT NULL DEFAULT 'stars_rounded';

-- Add completed_at field for Legacy of Success
ALTER TABLE goals 
ADD COLUMN IF NOT EXISTS completed_at VARCHAR;
