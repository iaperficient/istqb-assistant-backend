import os
import httpx
from openai import OpenAI
from fastapi import HTTPException
from typing import Optional
from app.rag.vector_store import get_vector_store_manager
import asyncio
from concurrent.futures import ThreadPoolExecutor

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

            # Query additional info from API endpoint if relevant
            api_info = ""
            # Temporarily disable API call to avoid blocking issues
            # async with httpx.AsyncClient() as client:
            #     # Example: query certifications endpoint if message contains keywords
            #     if any(keyword in message.lower() for keyword in ["certification", "certifications", "certificate", "certificates"]):
            #         try:
            #             response = await client.get("http://127.0.0.1:8000/certifications/")
            #             if response.status_code == 200:
            #                 data = response.json()
            #                 # Format data as string to include in prompt
            #                 api_info = "Additional certification info from API:\\n"
            #                 for cert in data:
            #                     api_info += f"- {cert.get('name', 'Unknown')} (Code: {cert.get('code', 'N/A')})\\n"
            #                 # If API info is available, prioritize it by ignoring RAG context
            #                 rag_result = {"context": "", "sources": [], "retrieval_successful": False}
            #         except Exception as e:
            #             api_info = f"Warning: Failed to fetch certification info from API: {str(e)}"

            system_prompt = """You are a virtual assistant specialized ONLY in these three ISTQB certifications:
1. Certified Tester Foundation Level (CTFL) v4.0
2. Certified Tester Testing with Generative AI (CT-GenAI)
3. Certified Tester AI Testing (CT-AI)

Instructions:

- Always answer in a friendly, respectful, and professional manner.
- Only use the embedded information about these three certifications. Do not invent or assume information from other ISTQB certifications or outside knowledge.
- If the conversation already makes clear which certification the user is referring to, answer based on that context. Only ask which certification the user means if it is genuinely ambiguous or not clear from the conversation history.
- If you don’t have enough information to answer from your embedded content, say so politely.
- Present your answers using plain text only, in a clean and organized way:
    - Use clear section titles, written in a separate line (for example: Overview, Purpose, Structure, etc.).
    - Use dashes or numbers for lists.
    - Separate each section with a blank line.
    - Do not use HTML, markdown, asterisks, or the # symbol.
- Always keep the conversation context: if the user is asking about a specific certification, continue answering about that certification unless the user explicitly changes to another certification.
- If the user asks for a document, provide the direct link if available.
"""

            messages = [{"role": "system", "content": system_prompt}]

            # Add RAG context if available
            if rag_result["context"]:
                messages.append({"role": "user", "content": f"Relevant context from ISTQB materials:\\n{rag_result['context']}"})

            # Add API info if available
            if api_info:
                messages.append({"role": "user", "content": api_info})

            # Add user-provided context if available
            if context:
                messages.extend(context)

            messages.append({"role": "user", "content": message})

            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                response = await loop.run_in_executor(
                    pool,
                    lambda: self.client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages,
                        max_tokens=1000,
                        temperature=0.4
                    )
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
