import os
from openai import OpenAI
from fastapi import HTTPException
from typing import Optional
from app.rag.vector_store import get_vector_store_manager

class OpenAIClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured"
            )
        self.client = OpenAI(api_key=api_key)
    
    async def generate_response(self, message: str, context: Optional[str] = None, certification_code: Optional[str] = None) -> dict:
        try:
            # Get RAG context
            vector_store = get_vector_store_manager()
            rag_result = {"context": "", "sources": [], "retrieval_successful": False}
            
            if vector_store.is_initialized():
                rag_result = vector_store.get_context_for_query(message, certification_code)
            
            system_prompt = """You are an ISTQB (International Software Testing Qualifications Board) assistant. 
            You help users understand software testing concepts, methodologies, and best practices according to ISTQB standards.
            Provide clear, accurate, and educational responses about software testing.
            
            Use the provided context information from ISTQB certification materials to enhance your responses when relevant, 
            but also rely on your training knowledge. If the context doesn't contain relevant information, 
            provide helpful responses based on your knowledge of ISTQB and software testing."""
            
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add RAG context if available
            if rag_result["context"]:
                messages.append({"role": "user", "content": f"Relevant context from ISTQB materials:\n{rag_result['context']}"})
            
            # Add user-provided context if available
            if context:
                messages.append({"role": "user", "content": f"Additional context: {context}"})
            
            messages.append({"role": "user", "content": message})
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return {
                "response": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "rag_info": {
                    "retrieval_successful": rag_result["retrieval_successful"],
                    "context_used": len(rag_result["context"]) > 0,
                    "num_sources": len(rag_result["sources"]),
                    "sources": rag_result["sources"][:3] if rag_result["sources"] else []
                }
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating response: {str(e)}"
            )