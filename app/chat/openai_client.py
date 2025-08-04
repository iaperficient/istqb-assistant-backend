import os
from openai import OpenAI
from fastapi import HTTPException
from typing import Optional
from app.rag.vector_store import get_vector_store_manager

class OpenAIClient:
    def __init__(self):
        api_key = "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"
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured"
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
            system_prompt = """You are a virtual assistant specialized ONLY in these three ISTQB certifications:
1. Certified Tester Foundation Level (CTFL) v4.0
2. Certified Tester Testing with Generative AI (CT-GenAI)
3. Certified Tester AI Testing (CT-AI)

Instructions:

- Always answer in a friendly, respectful, and professional manner.
- Only use the embedded information from the official syllabus documents of these three certifications. 
- Do not invent, paraphrase, summarize broadly, or assume information from other ISTQB certifications or external knowledge.
- If the user’s question is ambiguous, ask which certification it refers to.
- If the answer to the user’s question is not explicitly present in the documents, clearly respond with: 
  "The requested information is not available in the provided ISTQB syllabus content."

Formatting rules:

- Always reproduce the content exactly as written in the syllabus, without rewording or interpretation.
- You may segment content (split long paragraphs) for clarity, but do not rephrase or reformat any of the original wording.
- When possible, cite the source section from the document you retrieved the answer from. Example: (CT-GenAI v1.0, Section 2.3.2).
- Present answers using plain text only, in a clean and structured way:
  - Use clear section titles on their own line (e.g., Techniques, Examples).
  - Use dashes or numbers for lists.
  - Separate sections with a blank line.
  - Do not use HTML, markdown, bold, italics, or emoji.

Important:

- Always preserve the exact wording of the retrieved content unless explicitly told to summarize or explain.
- Maintain the conversational context across turns unless the user switches certification focus.
- If no matching chunk is found in the vector database, indicate that directly without attempting to guess or generate an answer.
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
