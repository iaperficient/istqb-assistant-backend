import hashlib
from typing import Optional
from sqlalchemy.orm import Session
from app.models.document import Document

def calculate_pdf_hash(pdf_content: bytes) -> str:
    """Calculate SHA256 hash of PDF content"""
    return hashlib.sha256(pdf_content).hexdigest()

def check_document_duplicate(db: Session, content_hash: str) -> Optional[Document]:
    """Check if a document with the same hash already exists"""
    return db.query(Document).filter(Document.content_hash == content_hash).first()

def get_duplicate_info(existing_doc: Document) -> dict:
    """Get information about duplicate document"""
    return {
        "is_duplicate": True,
        "existing_document": {
            "id": existing_doc.id,
            "title": existing_doc.title,
            "document_type": existing_doc.document_type,
            "certification_id": existing_doc.certification_id,
            "original_filename": existing_doc.original_filename,
            "created_at": existing_doc.created_at,
            "is_processed": existing_doc.is_processed
        },
        "message": f"Document with identical content already exists: '{existing_doc.title}' (ID: {existing_doc.id})"
    }