import os
import shutil
from typing import List, Dict, Any, Optional
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
import tempfile

# Set OpenAI API key from environment variable
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "")

class VectorStoreManager:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200,
            length_function=len,
        )
        self._vector_store = None
        self.embeddings = OpenAIEmbeddings()

    @property
    def vector_store(self):
        """Lazy initialization of vector store"""
        if self._vector_store is None:
            self._vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        return self._vector_store

    def add_pdf_to_rag(self, pdf_content: bytes, metadata: Dict[str, Any]) -> bool:
        """Add PDF content to RAG system"""
        try:
            # Create temporary file for PDF processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name

            try:
                # Load and process PDF
                loader = PyPDFLoader(temp_file_path)
                documents = loader.load()

                # Add metadata to each document
                for doc in documents:
                    doc.metadata.update(metadata)

                # Split documents into chunks
                chunks = self.text_splitter.split_documents(documents)

                # Add to vector store
                self.vector_store.add_documents(chunks)

                return True

            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)

        except Exception as e:
            print(f"Error adding PDF to RAG: {e}")
            return False

    def search_similar(self, query: str, k: int = 5, filter_dict: Optional[Dict] = None) -> List[Document]:
        """Search for similar documents"""
        try:
            if filter_dict:
                return self.vector_store.similarity_search(query, k=k, filter=filter_dict)
            else:
                return self.vector_store.similarity_search(query, k=k)
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return []

    def get_context_for_query(self, query: str, certification_code: Optional[str] = None) -> Dict[str, Any]:
        """Get relevant context for a query"""
        try:
            # Build filter if certification specified
            filter_dict = None
            if certification_code:
                filter_dict = {"certification_code": certification_code}

            # Search for relevant documents
            similar_docs = self.search_similar(query, k=5, filter_dict=filter_dict)

            if not similar_docs:
                print("No similar documents found for query.")
                return {
                    "context": "",
                    "sources": [],
                    "retrieval_successful": False
                }

            # Combine contexts
            contexts = []
            sources = []

            print(f"Found {len(similar_docs)} similar documents for query: {query}")
            for i, doc in enumerate(similar_docs):
                print(f"Document {i+1} content preview: {doc.page_content[:200]}...")
                contexts.append(doc.page_content)
                source_info = {
                    "certification_code": doc.metadata.get("certification_code", "Unknown"),
                    "document_type": doc.metadata.get("document_type", "Unknown"),
                    "title": doc.metadata.get("title", "Unknown")
                }
                if source_info not in sources:
                    sources.append(source_info)

            combined_context = "\n\n".join(contexts)

            print(f"Combined context length: {len(combined_context)} characters")

            return {
                "context": combined_context,
                "sources": sources,
                "retrieval_successful": True
            }

        except Exception as e:
            print(f"Error getting context: {e}")
            return {
                "context": "",
                "sources": [],
                "retrieval_successful": False
            }

    def delete_document_by_id(self, document_id: str) -> bool:
        """Delete specific document from vector store by document_id"""
        try:
            # Get all documents first to check what exists
            collection = self.vector_store._collection

            # Delete documents with specific document_id in metadata
            result = collection.delete(
                where={"document_id": {"$eq": str(document_id)}}
            )

            print(f"Deleted {len(result)} document chunks for document_id: {document_id}")
            return True

        except Exception as e:
            print(f"Error deleting document {document_id}: {e}")
            return False

    def delete_certification_documents(self, certification_code: str) -> bool:
        """Delete all documents for a specific certification"""
        try:
            collection = self.vector_store._collection

            # Delete all documents for this certification
            result = collection.delete(
                where={"certification_code": {"$eq": certification_code}}
            )

            print(f"Deleted documents for certification: {certification_code}")
            return True

        except Exception as e:
            print(f"Error deleting certification documents: {e}")
            return False

    def is_initialized(self) -> bool:
        """Check if vector store is initialized and has documents"""
        try:
            # Try to perform a simple search to see if there are any documents
            test_results = self.vector_store.similarity_search("test", k=1)
            return len(test_results) > 0
        except Exception:
            return False

# Global instance
_vector_store_manager = None

def get_vector_store_manager() -> VectorStoreManager:
    """Get global vector store manager instance"""
    global _vector_store_manager
    if _vector_store_manager is None:
        _vector_store_manager = VectorStoreManager()
    return _vector_store_manager
