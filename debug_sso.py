#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== Environment Variables ===")
print(f"GITHUB_CLIENT_ID: {os.getenv('GITHUB_CLIENT_ID')}")
print(f"GITHUB_CLIENT_SECRET: {os.getenv('GITHUB_CLIENT_SECRET')[:10]}..." if os.getenv('GITHUB_CLIENT_SECRET') else "None")
print(f"GITHUB_REDIRECT_URI: {os.getenv('GITHUB_REDIRECT_URI')}")

print("\n=== Testing SSO Manager ===")
from app.auth.sso import SSOManager

# Create a new SSO manager
sso_manager = SSOManager()

print(f"Available providers: {sso_manager.get_available_providers()}")
print(f"GitHub provider: {sso_manager.get_provider('github')}")

if sso_manager.get_provider('github'):
    github_provider = sso_manager.get_provider('github')
    print(f"GitHub client_id: {github_provider.client_id}")
    print(f"GitHub redirect_uri: {github_provider.redirect_uri}")
    print(f"Authorization URL: {github_provider.get_authorization_url()}")
else:
    print("GitHub provider not initialized!")
