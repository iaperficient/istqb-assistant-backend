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
try:
    from app.models.certification import Certification
    from app.models.document import Document
    MODELS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Certification models not available: {e}")
    MODELS_AVAILABLE = False
from app.auth.routes import router as auth_router
from app.auth.sso_routes import router as sso_router
try:
    from app.certification.routes import router as certification_router
    CERTIFICATION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Certification routes not available: {e}")
    CERTIFICATION_AVAILABLE = False
    certification_router = None
import uvicorn

# Create all tables
User.metadata.create_all(bind=engine)
if MODELS_AVAILABLE:
    Certification.metadata.create_all(bind=engine)
    Document.metadata.create_all(bind=engine)
    print("✅ Database tables created")

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
if CERTIFICATION_AVAILABLE:
    app.include_router(certification_router)
    print("✅ Certification routes loaded")
else:
    print("⚠️ Certification routes not available")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ISTQB Assistant API - SSO Test"}

if __name__ == "__main__":
    print("🚀 Starting ISTQB Assistant - SSO Test Server")
    print("📚 Visit http://localhost:8000/docs for API documentation")
    print("🔧 Visit http://localhost:8000/auth/sso/providers to see available SSO providers")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
