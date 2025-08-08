from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import engine
from app.models.user import User
from app.models.certification import Certification
from app.models.document import Document
from app.models.chat import ChatMessage
from app.auth.routes import router as auth_router
from app.auth.sso_routes import router as sso_router
from app.chat.routes import router as chat_router
from app.certification.routes import router as certification_router
from app.auth.admin_setup import create_admin_user
from app.chat.routes import chat_with_assistant

from dotenv import load_dotenv

load_dotenv()

import os
print(f"DEBUG: FULL OPENAI_API_KEY from environment: {os.getenv('OPENAI_API_KEY')}")


app = FastAPI(
    title="ISTQB Assistant API",
    description="An AI-powered assistant for ISTQB software testing concepts",
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
app.include_router(chat_router)
app.add_api_route("/api/chat",  chat_with_assistant, methods=["POST"], include_in_schema=False)
app.add_api_route("/api/chat/", chat_with_assistant, methods=["POST"], include_in_schema=False)
app.include_router(certification_router)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    try:
        # 1) Crear tablas (asegura que existan antes de crear el admin)
        for meta in (User.metadata, Certification.metadata, Document.metadata, ChatMessage.metadata):
            meta.create_all(bind=engine)

        # 2) Crear admin user
        admin_user = create_admin_user()
        if admin_user:
            print(f"✅ Admin user setup completed: {admin_user.username}")

    except Exception as e:
        print(f"❌ Error during application startup: {e}")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ISTQB Assistant API"}
