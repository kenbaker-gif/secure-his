from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database import Base

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    medical_history = Column(Text) # Sensitive content [cite: 4]
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)