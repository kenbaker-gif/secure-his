from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User, Role
from app.models.audit import AuditLog
from app.api.auth import get_current_user
from app.core.security import hash_password
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["System Administration"])

# --- SCHEMAS FOR DATA VALIDATION ---
class UserCreate(BaseModel):
    username: str
    password: str
    role_name: str

# --- PERMISSION CHECK ---
def admin_only(current_user: dict):
    if current_user["role"] != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access denied. Admin rights required."
        )
    return True

# --- ENDPOINTS ---

@router.get("/audit-logs")
def get_system_logs(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Enforces Integrity: Allows Admins to see who did what in the system."""
    admin_only(current_user)
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()

@router.post("/register-user")
def register_staff(user_data: UserCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Enforces Confidentiality: Create staff with Bcrypt hashed passwords."""
    admin_only(current_user)
    
    # 1. Check if username exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 2. Get the Role ID
    role = db.query(Role).filter(Role.role_name == user_data.role_name).first()
    if not role:
        raise HTTPException(status_code=400, detail="Role does not exist")
    
    # 3. Hash password and save
    new_user = User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        role_id=role.id
    )
    db.add(new_user)
    db.commit()
    return {"message": f"Successfully registered {user_data.username} as {user_data.role_name}"}

@router.get("/users")
def list_users(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Enforces Accountability: Admins manage active staff accounts."""
    admin_only(current_user)
    return db.query(User).all()

@router.delete("/users/{user_id}")
def deactivate_user(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Security Feature: Instantly revoke access (Revocation)."""
    admin_only(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} removed successfully"}