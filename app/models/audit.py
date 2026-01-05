from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # Who did it?
    action = Column(String)                           # What did they do? (e.g., LOGIN, VIEW, UPDATE)
    resource_id = Column(String, nullable=True)       # Which patient record was affected?
    ip_address = Column(String, nullable=True)        # Where did they do it from?
    timestamp = Column(DateTime, default=datetime.utcnow) # When did it happen?