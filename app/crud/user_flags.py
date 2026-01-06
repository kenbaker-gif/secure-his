from sqlalchemy.orm import Session
from app.models.user_flags import UserFlags


def get_flags(db: Session, user_id: int):
    return db.query(UserFlags).filter(UserFlags.user_id == user_id).first()


def set_must_change(db: Session, user_id: int, value: bool):
    flags = get_flags(db, user_id)
    if not flags:
        flags = UserFlags(user_id=user_id, must_change_password=value)
        db.add(flags)
    else:
        flags.must_change_password = value
        db.add(flags)
    db.commit()
    db.refresh(flags)
    return flags
