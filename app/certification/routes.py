import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.connection import get_db
from app.models.user import User
from app.models.certification import Certification
from app.models.document import Document
from app.schemas.certification import (
    CertificationCreate, CertificationResponse, CertificationWithDocuments,
    DocumentResponse, DocumentType
)
from app.auth.oauth2 import get_current_active_user
from app.auth.role_middleware import require_admin_checker
from app.rag.vector_store import get_vector_store_manager
from app.utils.document_utils import calculate_pdf_hash, check_document_duplicate, get_duplicate_info
import aiofiles

router = APIRouter(prefix="/certifications", tags=["certifications"])

# Directory to store uploaded PDFs
UPLOAD_DIR = "./uploads/certifications"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=CertificationResponse)
async def create_certification(
    certification: CertificationCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_checker)
):
    """Create a new certification (Admin only)"""
    # Check for duplicates
    existing = db.query(Certification).filter(Certification.code == certification.code).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Certification with code '{certification.code}' already exists"
        )
    
    db_certification = Certification(**certification.dict())
    db.add(db_certification)
    db.commit()
    db.refresh(db_certification)
    
    return db_certification

@router.get("/", response_model=List[CertificationResponse])
def get_certifications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all certifications"""
    certifications = db.query(Certification).filter(Certification.is_active == True).offset(skip).limit(limit).all()
    return certifications

@router.get("/{certification_id}", response_model=CertificationWithDocuments)
def get_certification(
    certification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get certification with its documents"""
    certification = db.query(Certification).filter(Certification.id == certification_id).first()
    if not certification:
        raise HTTPException(status_code=404, detail="Certification not found")
    return certification

@router.post("/{certification_id}/documents/syllabus")
async def upload_syllabus(
    certification_id: int,
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_checker)
):
    """Upload syllabus PDF for a certification"""
    return await _upload_document(certification_id, title, DocumentType.SYLLABUS, file, db)

@router.post("/{certification_id}/documents/sample-exam")
async def upload_sample_exam(
    certification_id: int,
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_checker)
):
    """Upload sample exam PDF for a certification"""
    return await _upload_document(certification_id, title, DocumentType.SAMPLE_EXAM, file, db)

async def _upload_document(
    certification_id: int,
    title: str,
    document_type: DocumentType,
    file: UploadFile,
    db: Session
) -> dict:
    """Helper function to upload and process documents"""
    # Verify certification exists
    certification = db.query(Certification).filter(Certification.id == certification_id).first()
    if not certification:
        raise HTTPException(status_code=404, detail="Certification not found")
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Read file content and calculate hash
    content = await file.read()
    content_hash = calculate_pdf_hash(content)
    
    # Check for duplicate content
    existing_doc = check_document_duplicate(db, content_hash)
    if existing_doc:
        return get_duplicate_info(existing_doc)
    
    # Create directory for this certification
    cert_dir = os.path.join(UPLOAD_DIR, certification.code)
    os.makedirs(cert_dir, exist_ok=True)
    
    # Generate file path
    file_path = os.path.join(cert_dir, f"{document_type.value}_{file.filename}")
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    # Create document record
    document = Document(
        certification_id=certification_id,
        title=title,
        document_type=document_type.value,
        file_path=file_path,
        original_filename=file.filename,
        content_hash=content_hash
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Process document for RAG
    rag_success = False
    rag_error = None
    
    try:
        vector_store = get_vector_store_manager()
        metadata = {
            "certification_code": certification.code,
            "certification_name": certification.name,
            "document_type": document_type.value,
            "title": title,
            "document_id": document.id
        }
        
        rag_success = vector_store.add_pdf_to_rag(content, metadata)
        if rag_success:
            document.is_processed = True
            db.commit()
            db.refresh(document)
        
    except Exception as e:
        rag_error = str(e)
        print(f"Warning: Failed to add document to RAG: {e}")
    
    # Prepare response message
    if rag_success:
        message = f"Document '{title}' uploaded and processed successfully into RAG"
    else:
        message = f"Document '{title}' uploaded but RAG processing failed"
        if rag_error:
            message += f": {rag_error}"
    
    return {
        "is_duplicate": False,
        "document": document,
        "message": message,
        "rag_processed": rag_success
    }

@router.get("/{certification_id}/documents", response_model=List[DocumentResponse])
def get_certification_documents(
    certification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all documents for a certification"""
    certification = db.query(Certification).filter(Certification.id == certification_id).first()
    if not certification:
        raise HTTPException(status_code=404, detail="Certification not found")
    
    documents = db.query(Document).filter(Document.certification_id == certification_id).all()
    return documents

@router.delete("/{certification_id}")
async def delete_certification(
    certification_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_checker)
):
    """Soft delete a certification (Admin only)"""
    certification = db.query(Certification).filter(Certification.id == certification_id).first()
    if not certification:
        raise HTTPException(status_code=404, detail="Certification not found")
    
    # Soft delete
    certification.is_active = False
    db.commit()
    
    # Clean up RAG data
    try:
        vector_store = get_vector_store_manager()
        vector_store.delete_certification_documents(certification.code)
    except Exception as e:
        print(f"Warning: Failed to clean up RAG data: {e}")
    
    return {"message": f"Certification {certification.code} has been deactivated"}

@router.post("/{certification_id}/reprocess")
async def reprocess_certification_documents(
    certification_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin_checker)
):
    """Reprocess all documents for a certification into RAG"""
    certification = db.query(Certification).filter(Certification.id == certification_id).first()
    if not certification:
        raise HTTPException(status_code=404, detail="Certification not found")
    
    documents = db.query(Document).filter(Document.certification_id == certification_id).all()
    
    vector_store = get_vector_store_manager()
    processed_count = 0
    
    for document in documents:
        try:
            if os.path.exists(document.file_path):
                # First, delete existing document from vector store
                vector_store.delete_document_by_id(str(document.id))
                
                # Then re-add it
                with open(document.file_path, 'rb') as f:
                    content = f.read()
                
                metadata = {
                    "certification_code": certification.code,
                    "certification_name": certification.name,
                    "document_type": document.document_type,
                    "title": document.title,
                    "document_id": document.id
                }
                
                success = vector_store.add_pdf_to_rag(content, metadata)
                if success:
                    document.is_processed = True
                    processed_count += 1
                
        except Exception as e:
            print(f"Failed to reprocess document {document.id}: {e}")
    
    db.commit()
    
    return {
        "message": f"Reprocessed {processed_count} documents for certification {certification.code}",
        "processed_count": processed_count,
        "total_documents": len(documents)
    }