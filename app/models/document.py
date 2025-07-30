from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    certification_id = Column(Integer, ForeignKey("certifications.id"), nullable=False)
    title = Column(String, nullable=False)
    document_type = Column(String, nullable=False)  # "syllabus" or "sample_exam"
    file_path = Column(String)  # Path to stored PDF file
    original_filename = Column(String)
    content_hash = Column(String, unique=True, index=True, nullable=False)  # SHA256 hash of PDF content
    content_text = Column(Text)  # Extracted text content
    is_processed = Column(Boolean, default=False)  # Whether it's been added to RAG
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    certification = relationship("Certification", back_populates="documents")
    
    def __repr__(self):
        return f"<Document(title='{self.title}', type='{self.document_type}')>"

# Add the relationship back to Certification
from app.models.certification import Certification
Certification.documents = relationship("Document", back_populates="certification")