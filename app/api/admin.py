from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, constr
from app.database import get_db
from app.models.user import User, Role
from app.crud.user import create_user
from app.api.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["System Administration"])

# --- Schemas ---
class UserCreate(BaseModel):
    username: constr(strip_whitespace=True, min_length=1)
    password: constr(min_length=1)
    role_name: constr(strip_whitespace=True, min_length=1)

class AdminReset(BaseModel):
    username: constr(strip_whitespace=True, min_length=1)
    temporary_password: constr(min_length=8)
# --- Admin permission check ---


def admin_only(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin rights required."
        )
    return current_user

# --- Endpoints ---
@router.post("/register-user")
def register_staff(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_only)
):
    # 1. Check username (strip and case-insensitive)
    desired_username = user_data.username.strip()
    existing_user = db.query(User).filter(func.lower(User.username) == desired_username.lower()).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # 2. Get role
    role = db.query(Role).filter(Role.role_name == user_data.role_name).first()
    if not role:
        raise HTTPException(status_code=400, detail="Role does not exist")

    # 3. Create user (store trimmed username)
    user = create_user(db, desired_username, user_data.password, role.id)
    return {"message": f"User '{user.username}' created with role '{role.role_name}'"}

@router.post('/reset-password')
def admin_reset_password(data: AdminReset, db: Session = Depends(get_db), current_user: dict = Depends(admin_only)):
    desired_username = data.username.strip()
    user = db.query(User).filter(func.lower(User.username) == desired_username.lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    from app.core.security import hash_password
    user.hashed_password = hash_password(data.temporary_password)
    db.add(user)
    db.commit()
    # Set must_change_password flag in user_flags table
    from app.crud.user_flags import set_must_change
    set_must_change(db, user.id, True)
    # Log admin reset
    from app.crud.audit import log_event
    # Log admin reset (user_id is None for operator-triggered event)
    log_event(db, None, f"PASSWORD_ADMIN_RESET: {user.username}")
    return {"message": f"Temporary password set for '{user.username}'. User must change password on next login."}

@router.get("/roles")
def list_roles(db: Session = Depends(get_db), current_user: dict = Depends(admin_only)):
    from app.models.user import Role
    roles = db.query(Role).all()
    return [{"id": r.id, "role_name": r.role_name} for r in roles]
@router.get("/audit-logs")
def list_audit_logs(db: Session = Depends(get_db), current_user: dict = Depends(admin_only)):
    from app.models.audit import AuditLog
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(200).all()
    return [
        {
            "id": l.id,
            "user_id": l.user_id,
            "action": l.action,
            "resource_id": l.resource_id,
            "ip_address": l.ip_address,
            "timestamp": l.timestamp.isoformat() if l.timestamp else None,
        }
        for l in logs
    ]

@router.get("/users")
def list_users(db: Session = Depends(get_db), current_user: dict = Depends(admin_only)):
    return db.query(User).all()
