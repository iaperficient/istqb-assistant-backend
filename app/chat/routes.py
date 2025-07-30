from fastapi import APIRouter, Depends, HTTPException
from app.schemas.chat import ChatMessage, ChatResponse, RAGInfo
from app.auth.oauth2 import get_current_active_user
from app.models.user import User
from app.chat.openai_client import OpenAIClient

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
async def chat_with_assistant(
    chat_message: ChatMessage,
    current_user: User = Depends(get_current_active_user)
):
    openai_client = OpenAIClient()
    
    result = await openai_client.generate_response(
        message=chat_message.message,
        context=chat_message.context,
        certification_code=chat_message.certification_code
    )
    
    return ChatResponse(
        response=result["response"],
        usage=result["usage"],
        rag_info=RAGInfo(**result["rag_info"]) if result.get("rag_info") else None
    )