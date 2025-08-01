import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.rag.vector_store import get_vector_store_manager

def test_retrieval(query: str):
    vector_store = get_vector_store_manager()
    results = vector_store.search_similar(query, k=5)
    if not results:
        print("No documents found for the query.")
        return
    print(f"Top {len(results)} documents for query: '{query}'")
    for i, doc in enumerate(results, 1):
        print(f"Document {i}:")
        print(f"Title: {doc.metadata.get('title', 'Unknown')}")
        print(f"Content snippet: {doc.page_content[:500]}")  # Print first 500 chars
        print("-" * 40)

if __name__ == "__main__":
    # Example query to test retrieval
    test_query = "software testing fundamentals"
    test_retrieval(test_query)
