#!/usr/bin/env python3
"""
Test script to verify SSO functionality
"""

import sys
import os
import asyncio

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.auth.sso import sso_manager

async def test_sso_configuration():
    """Test SSO configuration"""
    print("🔧 Testing SSO Configuration")
    print("=" * 40)
    
    # Check available providers
    providers = sso_manager.get_available_providers()
    print(f"📋 Available SSO providers: {providers}")
    
    if not providers:
        print("⚠️  No SSO providers configured")
        print("This is normal if you haven't added credentials to .env yet")
    else:
        print("✅ SSO providers are configured!")
        
        # Test each provider
        for provider_name in providers:
            provider = sso_manager.get_provider(provider_name)
            if provider:
                print(f"\n🔍 Testing {provider_name.upper()} provider:")
                print(f"   Client ID: {'Set' if provider.client_id else 'Not set'}")
                print(f"   Client Secret: {'Set' if provider.client_secret else 'Not set'}")
                print(f"   Redirect URI: {provider.redirect_uri}")
                
                # Get authorization URL
                try:
                    auth_url = provider.get_authorization_url()
                    print(f"   Auth URL: {auth_url[:100]}...")
                    print("   ✅ Provider is ready")
                except Exception as e:
                    print(f"   ❌ Error: {e}")

def test_database_schema():
    """Test if database schema is updated"""
    print("\n🗄️  Testing Database Schema")
    print("=" * 40)
    
    try:
        from app.database.connection import engine
        from sqlalchemy import text
        
        with engine.connect() as connection:
            result = connection.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]
            
            print(f"📋 Current columns: {columns}")
            
            required_columns = ['full_name', 'sso_provider']
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                print(f"❌ Missing columns: {missing_columns}")
                return False
            else:
                print("✅ Database schema is ready for SSO")
                return True
                
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def print_setup_instructions():
    """Print setup instructions for each provider"""
    print("\n📚 SSO Provider Setup Instructions")
    print("=" * 40)
    
    print("\n🔍 GOOGLE SSO:")
    print("1. Go to https://console.developers.google.com/")
    print("2. Create a new project or select an existing one")
    print("3. Enable the Google+ API")
    print("4. Create OAuth 2.0 credentials")
    print("5. Add authorized redirect URI: http://localhost:8000/auth/sso/google/callback")
    print("6. Copy Client ID and Client Secret to .env file")
    
    print("\n🔍 MICROSOFT SSO:")
    print("1. Go to https://portal.azure.com/")
    print("2. Navigate to Azure Active Directory > App registrations")
    print("3. Create a new registration")
    print("4. Add redirect URI: http://localhost:8000/auth/sso/microsoft/callback")
    print("5. Create a client secret in 'Certificates & secrets'")
    print("6. Copy Application (client) ID and client secret to .env file")
    
    print("\n🔍 GITHUB SSO:")
    print("1. Go to https://github.com/settings/applications/new")
    print("2. Create a new OAuth App")
    print("3. Set Authorization callback URL: http://localhost:8000/auth/sso/github/callback")
    print("4. Copy Client ID and Client Secret to .env file")

def print_api_endpoints():
    """Print available API endpoints"""
    print("\n🌐 Available SSO API Endpoints")
    print("=" * 40)
    print("GET  /auth/sso/providers                    - List available providers")
    print("GET  /auth/sso/{provider}/login             - Get authorization URL")
    print("GET  /auth/sso/{provider}/authorize         - Redirect to provider")
    print("GET  /auth/sso/{provider}/callback          - Handle provider callback")
    print("POST /auth/sso/{provider}/authenticate      - Authenticate with code")

async def main():
    """Main test function"""
    print("🚀 ISTQB Assistant - SSO Test Suite")
    print("=" * 50)
    
    # Test database schema
    db_ready = test_database_schema()
    
    # Test SSO configuration
    await test_sso_configuration()
    
    # Print setup instructions
    print_setup_instructions()
    
    # Print API endpoints
    print_api_endpoints()
    
    print("\n" + "=" * 50)
    if db_ready:
        print("✅ Database is ready for SSO")
    else:
        print("❌ Database needs migration")
    
    print("📝 Next steps:")
    print("1. Add SSO provider credentials to .env file")
    print("2. Restart the application")
    print("3. Test the endpoints using curl or Postman")
    print("4. Check /docs for interactive API documentation")

if __name__ == "__main__":
    asyncio.run(main())
