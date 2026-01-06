from sqlalchemy.orm import Session
from app.models.audit import AuditLog


def log_event(db: Session, user_id: int | None, action: str, resource_id: str = None, ip_address: str = None):
    db_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_id=resource_id,
        ip_address=ip_address,
    )
    db.add(db_log)
    db.commit()