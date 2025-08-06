#!/usr/bin/env python3
"""
Simple SSO Test Server for ISTQB Assistant
Runs on port 8001 to avoid conflicts
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.routes import router as auth_router
from app.auth.sso_routes import router as sso_router

def create_app():
    app = FastAPI(
        title="ISTQB Assistant - SSO Test",
        description="Simple SSO test server for ISTQB Assistant",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add routes
    app.include_router(auth_router)
    app.include_router(sso_router)
    
    @app.get("/")
    async def root():
        return {"message": "ISTQB Assistant SSO Test Server"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "message": "SSO Test Server is running"}
    
    return app

if __name__ == "__main__":
    print("🚀 Starting ISTQB Assistant - SSO Test Server on port 8001")
    print("📚 Visit http://localhost:8001/docs for API documentation")
    print("🔧 Visit http://localhost:8001/auth/sso/providers to see available SSO providers")
    
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
