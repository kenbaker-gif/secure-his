from sqlalchemy.orm import Session
from app.models.password_reset import PasswordResetToken
from datetime import datetime


def create_reset_token(db: Session, user_id: int, token_hash: str, expires_at: datetime):
    token = PasswordResetToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def get_valid_token_by_hash(db: Session, token_hash: str):
    now = datetime.utcnow()
    return db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash,
        PasswordResetToken.expires_at > now,
        PasswordResetToken.used_at == None
    ).first()


def mark_token_used(db: Session, token_id: int):
    token = db.query(PasswordResetToken).filter(PasswordResetToken.id == token_id).first()
    if token:
        token.used_at = datetime.utcnow()
        db.add(token)
        db.commit()
        db.refresh(token)
    return token


def purge_expired(db: Session):
    now = datetime.utcnow()
    db.query(PasswordResetToken).filter(PasswordResetToken.expires_at < now).delete()
    db.commit()
