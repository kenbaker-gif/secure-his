import os
os.environ['SKIP_DB_CREATE'] = 'true'
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, engine, Base
# Ensure all tables exist (apply new model changes)
# Import models so they are registered in metadata
from app.models.user_flags import UserFlags
from app.models.password_reset import PasswordResetToken
Base.metadata.create_all(bind=engine)
# Add missing column if needed for tests (legacy users table may be external)
from sqlalchemy import text
with engine.connect() as conn:
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS must_change_password boolean DEFAULT false;"))
    conn.execute(text("ALTER TABLE users ALTER COLUMN must_change_password SET DEFAULT false;"))
from app.models.user import User, Role
from app.crud.password_reset import create_reset_token, get_valid_token_by_hash
from app.core.security import hash_password
import secrets
from datetime import datetime, timedelta

client = TestClient(app)

def test_forgot_and_reset_flow():
    db = SessionLocal()

    # Ensure role
    role = db.query(Role).filter(Role.role_name == 'Doctor').first()
    if not role:
        role = Role(role_name='Doctor')
        db.add(role); db.commit(); db.refresh(role)

    # cleanup: remove any audit logs and flags before deleting user
    from app.models.audit import AuditLog
    from app.models.user_flags import UserFlags
    existing = db.query(User).filter(User.username == 'pw_user').all()
    from app.models.password_reset import PasswordResetToken
    for ex in existing:
        db.query(AuditLog).filter((AuditLog.user_id == ex.id) | (AuditLog.action.like('%pw_user%'))).delete(synchronize_session=False)
        db.query(UserFlags).filter(UserFlags.user_id == ex.id).delete(synchronize_session=False)
        db.query(PasswordResetToken).filter(PasswordResetToken.user_id == ex.id).delete(synchronize_session=False)
    db.query(User).filter(User.username == 'pw_user').delete(synchronize_session=False)
    db.commit()

    # create user
    user = User(username='pw_user', hashed_password=hash_password('oldpass'), role_id=role.id)
    db.add(user); db.commit(); db.refresh(user)

    # Simulate forgot-password flow by creating a token (tests don't rely on printed link)
    raw_token = secrets.token_urlsafe(24)
    token_hash = __import__('hashlib').sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(hours=1)
    create_reset_token(db, user.id, token_hash, expires_at)

    # Reset the password using the raw token
    r = client.post('/auth/reset-password', json={'token': raw_token, 'new_password': 'NewPassword123'})
    assert r.status_code == 200

    # Login with new password
    r = client.post('/auth/login', json={'username':'pw_user','password':'NewPassword123'})
    assert r.status_code == 200

    # Cleanup: remove audit logs, reset tokens, flags, then user
    from app.models.audit import AuditLog
    db.query(AuditLog).filter(AuditLog.action.like('%pw_user%')).delete(synchronize_session=False)
    db.query(AuditLog).filter(AuditLog.user_id == user.id).delete(synchronize_session=False)
    # remove any password reset tokens for this user
    from app.models.password_reset import PasswordResetToken
    db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).delete(synchronize_session=False)
    # remove flags
    from app.models.user_flags import UserFlags
    db.query(UserFlags).filter(UserFlags.user_id == user.id).delete(synchronize_session=False)
    db.query(User).filter(User.username == 'pw_user').delete(synchronize_session=False)
    db.commit()
    db.close()


def test_admin_reset_sets_flag_and_temp_password():
    db = SessionLocal()
    # ensure admin exists
    admin = db.query(User).filter(User.username == 'admin_user').first()
    assert admin is not None

    # Create a user to reset
    role = db.query(Role).filter(Role.role_name == 'Doctor').first()
    if not role:
        role = Role(role_name='Doctor')
        db.add(role); db.commit(); db.refresh(role)

    db.query(User).filter(User.username == 'to_reset').delete(synchronize_session=False)
    db.commit()
    user = User(username='to_reset', hashed_password=hash_password('start'), role_id=role.id)
    db.add(user); db.commit(); db.refresh(user)

    # Login as admin to get token
    r = client.post('/auth/login', json={'username':'admin_user','password':'admin123'})
    assert r.status_code == 200
    token = r.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Admin resets password
    r = client.post('/admin/reset-password', json={'username':'to_reset', 'temporary_password':'TempPass123'}, headers=headers)
    assert r.status_code == 200

    # Verify user has must_change_password True and can login with temp password
    u = db.query(User).filter(User.username == 'to_reset').first()
    from app.crud.user_flags import get_flags
    flags = get_flags(db, u.id)
    assert flags is not None and flags.must_change_password is True

    r = client.post('/auth/login', json={'username':'to_reset','password':'TempPass123'})
    assert r.status_code == 200
    assert r.json().get('must_change_password') is True

    # Cleanup: delete audit logs and flags before removing user
    from app.models.audit import AuditLog
    db.query(AuditLog).filter(AuditLog.action.like('%to_reset%')).delete(synchronize_session=False)
    db.query(AuditLog).filter(AuditLog.user_id == u.id).delete(synchronize_session=False)
    from app.models.password_reset import PasswordResetToken
    db.query(PasswordResetToken).filter(PasswordResetToken.user_id == u.id).delete(synchronize_session=False)
    from app.models.user_flags import UserFlags
    db.query(UserFlags).filter(UserFlags.user_id == u.id).delete(synchronize_session=False)
    db.query(User).filter(User.username == 'to_reset').delete(synchronize_session=False)
    db.commit()
    db.close()