from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.certification import Certification

def check_certifications():
    db = next(get_db())
    certifications = db.query(Certification).all()
    if not certifications:
        print("No certifications found in the database.")
        return
    print("Certifications in the database:")
    for cert in certifications:
        status = "Active" if cert.is_active else "Inactive"
        print(f"- ID: {cert.id}, Code: {cert.code}, Name: {cert.name}, Status: {status}")

if __name__ == "__main__":
    check_certifications()
