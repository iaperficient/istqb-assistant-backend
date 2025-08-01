import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()  # Load environment variables from .env file

from app.rag.vector_store import get_vector_store_manager

def test_retrieval_by_certification(cert_code: str):
    vector_store = get_vector_store_manager()
    results = vector_store.search_similar("test", k=5, filter_dict={"certification_code": cert_code})
    if not results:
        print(f"No documents found for certification_code: {cert_code}")
        return
    print(f"Top {len(results)} documents for certification_code: '{cert_code}'")
    for i, doc in enumerate(results, 1):
        print(f"Document {i}:")
        print(f"Title: {doc.metadata.get('title', 'Unknown')}")
        print(f"Content snippet: {doc.page_content[:500]}")
        print("-" * 40)

if __name__ == "__main__":
    test_retrieval_by_certification("SPECIALIST_GENAI")
    test_retrieval_by_certification("SPECIALIST_AI")
