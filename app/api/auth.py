from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.core.security import verify_password, create_access_token
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # 1. Find user in database
    user = db.query(User).filter(User.username == request.username).first()
    
    # 2. Verify password (Confidentiality check) [cite: 56]
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # 3. Create JWT Token with Role (RBAC enforcement) [cite: 47, 88]
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.role_name}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = "placeholder"):
    # This is a placeholder for your JWT decoding logic
    # It allows the app to start without crashing
    return {"id": 1, "username": "doctor_test", "role": "Doctor"}