#!/usr/bin/env python3
"""
Minimal SSO Test Server for ISTQB Assistant
Excludes chat/vector store components that require newer SQLite
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.routes import router as auth_router
from app.auth.sso_routes import router as sso_router
from app.database.connection import engine
from app.models.user import User
from app.auth.admin_setup import create_admin_user
from dotenv import load_dotenv

load_dotenv()

# Create user table only (no chat/vector store)
User.metadata.create_all(bind=engine)

app = FastAPI(
    title="ISTQB Assistant - SSO Test",
    description="Minimal SSO test server for ISTQB Assistant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only auth and SSO routes
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
    except Exception as e:
        print(f"❌ Error during application startup: {e}")

@app.get("/")
def root():
    return {"message": "ISTQB Assistant SSO Test Server", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ISTQB Assistant SSO Test"}

if __name__ == "__main__":
    print("🚀 Starting ISTQB Assistant - Minimal SSO Test Server")
    print("📚 Visit http://localhost:8000/docs for API documentation")
    print("🔧 Visit http://localhost:8000/auth/sso/providers to see available SSO providers")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
