from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.database.connection import Base

class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)  # e.g., "CTFL-v4.0"
    name = Column(String, nullable=False)  # e.g., "Certified Tester Foundation Level"
    url = Column(String, nullable=False)  # Original certification URL
    description = Column(Text)
    version = Column(String)  # e.g., "v4.0"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Certification(code='{self.code}', name='{self.name}')>"