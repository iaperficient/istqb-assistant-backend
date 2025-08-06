#!/usr/bin/env python3
"""
Migration script to fix SSO user creation by making hashed_password nullable
"""

import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

def fix_sso_database():
    """Fix the database schema for SSO users"""
    db_path = "istqb_assistant.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Fixing database schema for SSO users...")
        
        # Check current schema
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("📋 Current users table schema:")
        for col in columns:
            print(f"  - {col[1]}: {col[2]} (nullable: {not bool(col[3])})")
        
        # Create a temporary table with the correct schema
        print("\n🔄 Creating temporary table with correct schema...")
        cursor.execute("""
            CREATE TABLE users_temp (
                id INTEGER PRIMARY KEY,
                username VARCHAR UNIQUE NOT NULL,
                email VARCHAR UNIQUE NOT NULL,
                hashed_password VARCHAR,  -- Made nullable
                full_name VARCHAR,
                sso_provider VARCHAR,
                role VARCHAR NOT NULL DEFAULT 'USER',
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME
            )
        """)
        
        # Copy existing data
        print("📦 Copying existing data...")
        cursor.execute("""
            INSERT INTO users_temp (id, username, email, hashed_password, full_name, sso_provider, role, is_active, created_at, updated_at)
            SELECT id, username, email, hashed_password, full_name, sso_provider, role, is_active, created_at, updated_at
            FROM users
        """)
        
        # Drop old table and rename new one
        print("🔄 Replacing old table...")
        cursor.execute("DROP TABLE users")
        cursor.execute("ALTER TABLE users_temp RENAME TO users")
        
        # Recreate indexes
        print("📇 Recreating indexes...")
        cursor.execute("CREATE UNIQUE INDEX ix_users_username ON users (username)")
        cursor.execute("CREATE UNIQUE INDEX ix_users_email ON users (email)")
        cursor.execute("CREATE INDEX ix_users_id ON users (id)")
        
        # Commit changes
        conn.commit()
        
        print("\n✅ Database schema fixed successfully!")
        print("🎉 SSO users can now be created without passwords!")
        
        # Verify the fix
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("\n📋 Updated users table schema:")
        for col in columns:
            print(f"  - {col[1]}: {col[2]} (nullable: {not bool(col[3])})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting SSO Database Migration")
    success = fix_sso_database()
    if success:
        print("\n✅ Migration completed successfully!")
        print("🔄 Please restart your backend server to apply changes.")
    else:
        print("\n❌ Migration failed!")
