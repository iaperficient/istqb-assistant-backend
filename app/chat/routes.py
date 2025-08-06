from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.chat import ChatMessage, ChatResponse, RAGInfo
from app.auth.oauth2 import get_current_active_user
from app.models.user import User
from app.models.chat import ChatMessage as ChatMessageModel
from app.chat.openai_client import OpenAIClient
from app.database.connection import get_db
from typing import List
import logging

router = APIRouter(prefix="/chat", tags=["chat"])

@router.delete("/history")
async def delete_chat_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        deleted = db.query(ChatMessageModel).filter(ChatMessageModel.user_id == current_user.id).delete()
        db.commit()
        return {"detail": f"Deleted {deleted} chat messages for user {current_user.username}"}
    except Exception as e:
        logging.error(f"Error deleting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def format_chat_history_for_openai(messages: List[ChatMessageModel]) -> list:
    formatted = []
    for msg in messages:
        role = "user" if msg.sender == "user" else "assistant"
        formatted.append({"role": role, "content": msg.message})
    return formatted

@router.get("/history", response_model=List[ChatMessage])
async def get_chat_history(
    conversation_id: str = Query(None, description="Conversation ID to filter messages"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        query = db.query(ChatMessageModel).filter(ChatMessageModel.user_id == current_user.id)
        if conversation_id:
            query = query.filter(ChatMessageModel.conversation_id == conversation_id)
        history = query.order_by(ChatMessageModel.timestamp.asc()).all()
        return [ChatMessage(message=msg.message, context=None, certification_code=None) for msg in history]
    except Exception as e:
        logging.error(f"Error fetching chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/", response_model=ChatResponse)
async def chat_with_assistant(
    chat_message: ChatMessage,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        logging.info(f"DEBUG: Received message from user {current_user.username}: {chat_message.message}")

        conversation_id = chat_message.conversation_id or "default_conversation"

        # 1. Recupera historial anterior (últimos 19 mensajes)
        history = db.query(ChatMessageModel)\
            .filter(ChatMessageModel.user_id == current_user.id)\
            .filter(ChatMessageModel.conversation_id == conversation_id)\
            .order_by(ChatMessageModel.timestamp.asc())\
            .all()
        history = history[-19:]  # Deja espacio para el mensaje actual

        # 2. Formatea historial
        context_list = format_chat_history_for_openai(history)

        # 3. Guarda el mensaje actual del usuario ANTES de llamar al modelo
        user_msg = ChatMessageModel(
            user_id=current_user.id,
            conversation_id=conversation_id,
            sender="user",
            message=chat_message.message
        )
        db.add(user_msg)
        try:
            db.commit()
            logging.info("User message committed to database")
        except Exception as commit_error:
            logging.error(f"Error committing user message: {commit_error}")
            db.rollback()
            raise
        db.refresh(user_msg)

        # 4. Agrega el mensaje actual al historial
        context_list.append({"role": "user", "content": chat_message.message})

        # 5. Llama al modelo con todo el historial (incluyendo el mensaje actual)
        openai_client = OpenAIClient()
        import pprint
        print("\n==== MENSAJES ENVIADOS AL MODELO ====")
        pprint.pprint(context_list)
        print("======================================\n")

        result = await openai_client.generate_response(
            message=chat_message.message,
            context=context_list,
            certification_code=chat_message.certification_code
        )

        # 6. Guarda respuesta del bot
        assistant_msg = ChatMessageModel(
            user_id=current_user.id,
            conversation_id=conversation_id,
            sender="assistant",
            message=result["response"]
        )
        db.add(assistant_msg)
        try:
            db.commit()
            logging.info("Assistant message committed to database")
        except Exception as commit_error:
            logging.error(f"Error committing assistant message: {commit_error}")
            db.rollback()
            raise
        db.refresh(assistant_msg)

        logging.info(f"Assistant response sent to user {current_user.username}")

        return ChatResponse(
            response=result["response"],
            usage=result["usage"],
            rag_info=RAGInfo(**result["rag_info"]) if result.get("rag_info") else None
        )
    except Exception as e:
        logging.error(f"Error in chat_with_assistant: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
