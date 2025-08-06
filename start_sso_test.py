#!/usr/bin/env python3
"""
Simple startup script to test SSO functionality without ChromaDB
"""

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import engine
from app.models.user import User
from app.auth.routes import router as auth_router
from app.auth.sso_routes import router as sso_router
from app.auth.admin_setup import create_admin_user
from dotenv import load_dotenv

load_dotenv()

# Create all tables
User.metadata.create_all(bind=engine)

app = FastAPI(
    title="ISTQB Assistant API - SSO Test",
    description="Testing SSO functionality for ISTQB Assistant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only auth and SSO routes for testing
app.include_router(auth_router)
app.include_router(sso_router)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    try:
        # Create admin user
        admin_user = create_admin_user()
        if admin_user:
            print(f"✅ Admin user setup completed: {admin_user.username}")
        
        # Test SSO configuration
        from app.auth.sso import sso_manager
        providers = sso_manager.get_available_providers()
        if providers:
            print(f"✅ SSO providers configured: {providers}")
        else:
            print("⚠️  No SSO providers configured (check .env file)")
            
    except Exception as e:
        print(f"❌ Error during application startup: {e}")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ISTQB Assistant API - SSO Test"}

@app.get("/")
def root():
    return {
        "message": "ISTQB Assistant - SSO Test Server",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "auth": "/auth/*",
            "sso": "/auth/sso/*"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting ISTQB Assistant - SSO Test Server")
    print("📚 Visit http://localhost:8000/docs for API documentation")
    print("🔧 Visit http://localhost:8000/auth/sso/providers to see available SSO providers")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
