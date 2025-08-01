import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.rag.vector_store import get_vector_store_manager

def process_pdf(file_path: str, metadata: dict):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False

    with open(file_path, "rb") as f:
        content = f.read()

    vector_store = get_vector_store_manager()
    success = vector_store.add_pdf_to_rag(content, metadata)
    if success:
        print(f"Successfully processed and vectorized PDF: {file_path}")
    else:
        print(f"Failed to process PDF: {file_path}")
    return success

if __name__ == "__main__":
    # Define the path to the PDF file
    pdf_path = "uploads/certifications/Foundation Level/ISTQB_CTFL_Syllabus_v4.0.1.pdf"

    # Define metadata for the PDF
    metadata = {
        "certification_code": "FOUNDATION_LEVEL",
        "certification_name": "Foundation Level",
        "document_type": "SYLLABUS",
        "title": "ISTQB CTFL Syllabus v4.0.1",
        "document_id": "manual_process_001"
    }

    process_pdf(pdf_path, metadata)
