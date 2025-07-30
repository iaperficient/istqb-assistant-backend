from pydantic import BaseModel
from typing import Optional, List

class RAGInfo(BaseModel):
    retrieval_successful: bool
    context_used: bool
    num_sources: int
    sources: List[dict]

class ChatMessage(BaseModel):
    message: str
    context: Optional[str] = None
    certification_code: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    usage: Optional[dict] = None
    rag_info: Optional[RAGInfo] = None