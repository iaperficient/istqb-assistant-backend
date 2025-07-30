from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, List
from enum import Enum

class DocumentType(str, Enum):
    SYLLABUS = "syllabus"
    SAMPLE_EXAM = "sample_exam"

class CertificationBase(BaseModel):
    code: str
    name: str
    url: str
    description: Optional[str] = None
    version: Optional[str] = None

class CertificationCreate(CertificationBase):
    pass

class CertificationResponse(CertificationBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    title: str
    document_type: DocumentType

class DocumentCreate(DocumentBase):
    certification_id: int

class DocumentResponse(DocumentBase):
    id: int
    certification_id: int
    file_path: Optional[str] = None
    original_filename: Optional[str] = None
    content_hash: str
    is_processed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CertificationWithDocuments(CertificationResponse):
    documents: List[DocumentResponse] = []