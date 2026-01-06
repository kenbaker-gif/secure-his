from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from pydantic import BaseModel, constr
import secrets
import hashlib
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.core.security import verify_password, create_access_token, SECRET_KEY, ALGORITHM, hash_password
from app.crud.audit import log_event
from app.crud.password_reset import create_reset_token, get_valid_token_by_hash, mark_token_used
from app.crud.audit import log_event

router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- Pydantic schema for login ---
class LoginRequest(BaseModel):
    username: constr(strip_whitespace=True, min_length=1)
    password: str

class ForgotPasswordRequest(BaseModel):
    username: constr(strip_whitespace=True, min_length=1)

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: constr(min_length=8)

# --- OAuth2 for FastAPI ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- LOGIN ENDPOINT ---
@router.post("/login")
def login(login_req: LoginRequest, db: Session = Depends(get_db), request: Request = None):
    # capture client IP if available
    client_ip = None
    if request and getattr(request, 'client', None):
        client_ip = request.client.host

    # 1. Find user in database
    user = db.query(User).filter(User.username == login_req.username).first()

    # 2. Verify password
    if not user or not verify_password(login_req.password, user.hashed_password):
        # Log failed login attempt (username may not exist)
        log_event(db, None, f"LOGIN_FAILED: {login_req.username}", ip_address=client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    # 3. Log success and create JWT with role
    log_event(db, user.id, "LOGIN_SUCCESS", ip_address=client_ip)

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.role_name}
    )

    # Read must_change_password from flags table (keeps app independent of external 'users' table schema)
    try:
        from app.crud.user_flags import get_flags
        flags = get_flags(db, user.id)
        must_change = bool(flags.must_change_password) if flags else False
    except Exception:
        must_change = False

    return {"access_token": access_token, "token_type": "bearer", "must_change_password": must_change}

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    # Use username to look up account; in production use email and send link
    user = db.query(User).filter(User.username == req.username).first()
    if user:
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expires_at = datetime.utcnow() + timedelta(hours=1)
        create_reset_token(db, user.id, token_hash, expires_at)
        log_event(db, user.id, "PASSWORD_RESET_REQUESTED")
        # TODO: send email. For now, print the reset link so it can be used in tests/dev
        print(f"Password reset link (one-time): http://example/reset?token={raw_token}")
    # Always return a neutral response
    return {"message": "If an account exists we sent password reset instructions."}

@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(req.token.encode()).hexdigest()
    token_obj = get_valid_token_by_hash(db, token_hash)
    if not token_obj:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == token_obj.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")

    # Update password and mark token used
    user.hashed_password = hash_password(req.new_password)
    user.must_change_password = False
    db.add(user)
    db.commit()
    mark_token_used(db, token_obj.id)
    log_event(db, user.id, "PASSWORD_RESET_COMPLETED")

    return {"message": "Password reset successful"}

# --- GET CURRENT USER FROM TOKEN ---
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return {"username": username, "role": role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
