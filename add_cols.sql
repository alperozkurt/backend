-- Add new columns for the Profile feature
ALTER TABLE users ADD COLUMN job_type VARCHAR;
ALTER TABLE users ADD COLUMN monthly_salary FLOAT;
