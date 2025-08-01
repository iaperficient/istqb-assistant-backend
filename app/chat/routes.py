from fastapi import APIRouter, Depends, HTTPException
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

def format_chat_history_for_openai(messages: List[ChatMessageModel]) -> list:
    formatted = []
    for msg in messages:
        role = "user" if msg.sender == "user" else "assistant"
        formatted.append({"role": role, "content": msg.message})
    return formatted

@router.get("/history", response_model=List[ChatMessage])
async def get_chat_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        history = db.query(ChatMessageModel)\
            .filter(ChatMessageModel.user_id == current_user.id)\
            .order_by(ChatMessageModel.timestamp.asc())\
            .all()
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
        logging.info(f"Received message from user {current_user.username}: {chat_message.message}")

        # Retrieve last 20 messages for the user ordered by timestamp ascending
        # Use conversation_id to filter messages for the same conversation
        conversation_id = chat_message.conversation_id or "default_conversation"
        history = db.query(ChatMessageModel)\
            .filter(ChatMessageModel.user_id == current_user.id)\
            .filter(ChatMessageModel.conversation_id == conversation_id)\
            .order_by(ChatMessageModel.timestamp.asc())\
            .all()
        
        # Limit to last 20 messages
        history = history[-20:]
        
        # Format history into context list for OpenAI
        context_list = format_chat_history_for_openai(history)
        
        # Append current user message to context
        context_list.append({"role": "user", "content": chat_message.message})
        
        import pprint
        openai_client = OpenAIClient()

        print("\n==== MENSAJES ENVIADOS AL MODELO ====")
        pprint.pprint(context_list)
        print("======================================\n")
        
        result = await openai_client.generate_response(
            message=chat_message.message,
            context=context_list,
            certification_code=chat_message.certification_code
        )
        
        # Save user message
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
        
        # Save assistant response
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
