#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import engine
from app.models.user import User
from app.auth.routes import router as auth_router
from app.auth.sso_routes import router as sso_router

# Create all tables
User.metadata.create_all(bind=engine)
print("✅ Database tables created")

app = FastAPI(
    title="ISTQB Assistant API",
    description="ISTQB Assistant API with SSO authentication",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(sso_router)

@app.get("/")
def read_root():
    return {"message": "ISTQB Assistant API", "status": "running", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ISTQB Assistant API"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting ISTQB Assistant API")
    print("📚 Visit /docs for API documentation")
    print("🔧 Visit /auth/sso/providers to see available SSO providers")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
