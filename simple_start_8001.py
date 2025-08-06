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
import uvicorn

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

app.include_router(auth_router)
app.include_router(sso_router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ISTQB Assistant API - SSO Test"}

if __name__ == "__main__":
    print("🚀 Starting ISTQB Assistant - SSO Test Server on port 8001")
    print("📚 Visit http://localhost:8001/docs for API documentation")
    print("🔧 Visit http://localhost:8001/auth/sso/providers to see available SSO providers")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
