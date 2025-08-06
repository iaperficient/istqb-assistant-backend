import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()  # Load environment variables from .env file

from app.rag.vector_store import get_vector_store_manager

def list_all_documents():
    vector_store = get_vector_store_manager()
    # Access the underlying collection directly
    collection = vector_store.vector_store._collection
    try:
        # Get all documents in the collection
        all_docs = collection.get(include=["documents", "metadatas"])
        documents = all_docs.get("documents", [])
        metadatas = all_docs.get("metadatas", [])
        if not documents:
            print("No documents found in the vector store.")
            return
        for i, (doc, meta) in enumerate(zip(documents, metadatas), 1):
            print(f"Document {i}:")
            print(f"Metadata: {meta}")
            print(f"Content snippet: {doc[:500]}")
            print("-" * 40)
    except Exception as e:
        print(f"Error retrieving documents: {e}")

if __name__ == "__main__":
    list_all_documents()
