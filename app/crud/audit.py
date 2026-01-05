from sqlalchemy.orm import Session
from app.models.audit import AuditLog

def log_event(db: Session, user_id: int, action: str, resource_id: str = None):
    db_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_id=resource_id
    )
    db.add(db_log)
    db.commit()