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
    import argparse
    parser = argparse.ArgumentParser(description="Embed a PDF into the vector store with metadata.")
    parser.add_argument("pdf_path", type=str, help="Path to the PDF file.")
    parser.add_argument("--certification_code", type=str, required=True, help="Certification code.")
    parser.add_argument("--certification_name", type=str, required=True, help="Certification name.")
    parser.add_argument("--document_type", type=str, required=True, help="Document type.")
    parser.add_argument("--title", type=str, required=True, help="Document title.")
    parser.add_argument("--document_id", type=str, required=True, help="Document ID.")

    args = parser.parse_args()
    metadata = {
        "certification_code": args.certification_code,
        "certification_name": args.certification_name,
        "document_type": args.document_type,
        "title": args.title,
        "document_id": args.document_id
    }
    process_pdf(args.pdf_path, metadata)
