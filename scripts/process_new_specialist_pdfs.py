import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()  # Load environment variables from .env file

from scripts.process_pdf import process_pdf

specialist_pdfs = [
    {
        "file_path": "uploads/certifications/Specialist/CT-GenAI-Syllabus-v1.0.pdf",
        "metadata": {
            "certification_code": "SPECIALIST_GENAI",
            "certification_name": "Specialist GenAI",
            "document_type": "SYLLABUS",
            "title": "CT-GenAI Syllabus v1.0",
            "document_id": "specialist_genai_001"
        }
    },
    {
        "file_path": "uploads/certifications/Specialist/ISTQB_CT-AI_Syllabus_v1.0_mghocmT.pdf",
        "metadata": {
            "certification_code": "SPECIALIST_AI",
            "certification_name": "Specialist AI",
            "document_type": "SYLLABUS",
            "title": "ISTQB CT-AI Syllabus v1.0",
            "document_id": "specialist_ai_001"
        }
    }
]

for pdf in specialist_pdfs:
    print(f"Processing {pdf['file_path']}...")
    success = process_pdf(pdf["file_path"], pdf["metadata"])
    if not success:
        print(f"Failed to process {pdf['file_path']}")
