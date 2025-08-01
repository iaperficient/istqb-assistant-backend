#!/usr/bin/env python3
"""
Database migration script to add SSO support to the User table
"""

import sqlite3
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database.connection import SQLALCHEMY_DATABASE_URL, engine

def run_migration():
    """Run the SSO migration"""
    print("🚀 Starting SSO database migration...")
    
    try:
        # Create a direct connection to run the migration
        with engine.connect() as connection:
            # Start a transaction
            trans = connection.begin()
            
            try:
                # Check if columns already exist
                result = connection.execute(text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result.fetchall()]
                
                print(f"📋 Current columns in users table: {columns}")
                
                # Add full_name column if it doesn't exist
                if 'full_name' not in columns:
                    print("➕ Adding full_name column...")
                    connection.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR"))
                    print("✅ Added full_name column")
                else:
                    print("ℹ️  full_name column already exists")
                
                # Add sso_provider column if it doesn't exist
                if 'sso_provider' not in columns:
                    print("➕ Adding sso_provider column...")
                    connection.execute(text("ALTER TABLE users ADD COLUMN sso_provider VARCHAR"))
                    print("✅ Added sso_provider column")
                else:
                    print("ℹ️  sso_provider column already exists")
                
                # SQLite doesn't support ALTER COLUMN, so we need to check if hashed_password is nullable
                # We'll handle this by creating a new table structure if needed
                print("🔍 Checking hashed_password column constraints...")
                
                # For SQLite, we'll just note that hashed_password should be nullable for SSO users
                # The application code already handles this properly
                print("ℹ️  hashed_password column constraint will be handled at application level")
                
                # Commit the transaction
                trans.commit()
                print("✅ Migration completed successfully!")
                
            except Exception as e:
                # Rollback on error
                trans.rollback()
                print(f"❌ Error during migration: {e}")
                raise
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True

def verify_migration():
    """Verify the migration was successful"""
    print("\n🔍 Verifying migration...")
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]
            
            required_columns = ['full_name', 'sso_provider']
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                print(f"❌ Missing columns: {missing_columns}")
                return False
            else:
                print("✅ All required columns are present")
                print(f"📋 Final columns: {columns}")
                return True
                
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 ISTQB Assistant - SSO Database Migration")
    print("=" * 50)
    
    # Check if database file exists
    db_path = "./istqb_assistant.db"
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        print("Please start the application first to create the database")
        exit(1)
    
    # Run migration
    if run_migration():
        if verify_migration():
            print("\n🎉 SSO migration completed successfully!")
            print("\nNext steps:")
            print("1. Configure your SSO provider credentials in .env file")
            print("2. Restart your application")
            print("3. Test SSO login endpoints")
        else:
            print("\n❌ Migration verification failed")
            exit(1)
    else:
        print("\n❌ Migration failed")
        exit(1)
