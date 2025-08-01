-- Add SSO support fields to users table
-- Run this migration if you have existing users table

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS full_name VARCHAR;

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS sso_provider VARCHAR;

-- Make hashed_password nullable for SSO users
ALTER TABLE users 
ALTER COLUMN hashed_password DROP NOT NULL;
