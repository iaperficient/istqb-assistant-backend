import os
from openai import OpenAI
from fastapi import HTTPException
from typing import Optional
from app.rag.vector_store import get_vector_store_manager

class OpenAIClient:
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured (missing OPENAI_API_KEY env var)"
            )
        self.client = OpenAI(api_key=api_key)

    async def generate_response(self, message: str, context: Optional[list] = None, certification_code: Optional[str] = None) -> dict:
        import re
        import logging
        try:
            # Get RAG context
            vector_store = get_vector_store_manager()
            rag_result = {"context": "", "sources": [], "retrieval_successful": False}
            if vector_store.is_initialized():
                rag_result = vector_store.get_context_for_query(message, certification_code)

            # Build system prompt
            system_prompt = """You are a virtual assistant specialized in ISTQB certifications.

Instructions:

- Always answer in a friendly, respectful, and professional manner.
- Only use the embedded information from official ISTQB certification materials. Do not invent or assume information from other sources or your own knowledge if not present in the context.

- Before searching for an answer, always review the user's question. If the question contains spelling mistakes, typos, or unclear wording, silently correct and clarify it to best reflect the user's intent. Then, use this corrected and clarified version of the question for all internal processing and information retrieval, even if you do not display the correction to the user.

- When reviewing the user's question, always silently correct any typos or unclear wording to the most probable intent, based on the available ISTQB certifications and terminology. If the user's input can be reasonably mapped to a specific ISTQB certification (e.g., "genai" means "Generative AI"), assume that mapping automatically, and proceed without asking the user for clarification. Only ask the user to clarify if there is genuine ambiguity that cannot be resolved by context or common sense.

- If the user asks about "Business Outcomes" or similar and the relevant context includes a table or list of outcomes with codes (e.g., GenAI-BO1, CTFL-BO2, etc.), respond by copying the entire table and codes exactly as presented in the reference material. Do NOT summarize, rephrase, or omit any item.

- If the conversation already makes clear which certification or document the user is referring to, answer based on that context. Only ask which certification the user means if it is genuinely ambiguous or not clear from the conversation history.

- If you don’t have enough information to answer from your embedded content, say so politely.

- Always display the reference(s) used to answer the question. At the end of every answer, clearly indicate the section number if available of the source(s) from which the answer was obtained.

- Present your answers using plain text only, in a clean and organized way:
    - Use clear section titles, written on a separate line (for example: Overview, Purpose, Structure, etc.).
    - Use  numbers for lists.
    - Separate each section with a blank line.
    - Do not use HTML, markdown, asterisks, or * the # symbol.

- Always keep the conversation context: if the user is asking about a specific certification, continue answering about that certification unless the user explicitly changes to another certification.

- If the user asks for a document, provide the direct link if available.
"""
            # Assemble messages
            messages = [{"role": "system", "content": system_prompt}]

            # Add RAG context if available
            if rag_result["context"]:
                messages.append({
                    "role": "assistant",
                    "content": f"Relevant ISTQB context:\n{rag_result['context']}"
                })

            # Add full conversation history (including latest user message)
            if context:
                messages.extend(context)

            # Call OpenAI API synchronously
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1000,
                temperature=0.4
            )

            # Validate citations in response
            response_text = response.choices[0].message.content
            sources = rag_result.get("sources", [])
            source_titles = [source.get("title", "").lower() for source in sources]

            # Extract citations like (CT-GenAI v1.0, Section 2.2.2)
            citation_pattern = re.compile(r"\(([^)]+)\)")
            citations = citation_pattern.findall(response_text)

            invalid_citations = []
            for citation in citations:
                # Check if citation contains any known source title substring
                if not any(title in citation.lower() for title in source_titles):
                    invalid_citations.append(citation)

            if invalid_citations:
                logging.warning(f"Invalid citations found in response: {invalid_citations}")
                # Optionally, modify response to remove or flag invalid citations
                # For now, just log the warning

            logging.info(f"Response generated with {len(citations)} citations, {len(invalid_citations)} invalid.")

            return {
                "response": response_text,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else None,
                    "completion_tokens": response.usage.completion_tokens if response.usage else None,
                    "total_tokens": response.usage.total_tokens if response.usage else None
                },
                "rag_info": {
                    "retrieval_successful": rag_result["retrieval_successful"],
                    "context_used": bool(rag_result["context"]),
                    "num_sources": len(sources),
                    "sources": sources[:3] if sources else []
                }
            }
        except Exception as e:
            import logging
            logging.error(f"Error generating response: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error generating response: {str(e)}"
            )
