import os
os.environ['SKIP_DB_CREATE'] = 'true'
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, engine, Base
# Ensure DB schema is up to date for tests
# Import new models so they register with the Base metadata
from app.models.user_flags import UserFlags
from app.models.password_reset import PasswordResetToken
Base.metadata.create_all(bind=engine)
# Apply minimal schema migrations required for tests (legacy users table may be external)
from sqlalchemy import text
with engine.connect() as conn:
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS must_change_password boolean DEFAULT false;"))
    conn.execute(text("ALTER TABLE users ALTER COLUMN must_change_password SET DEFAULT false;"))
from app.models.user import User, Role
from app.models.audit import AuditLog
from app.crud.user import create_user
from sqlalchemy import func

client = TestClient(app)

def test_login_audit_logs():
    db = SessionLocal()
    # Ensure a Doctor role exists
    role = db.query(Role).filter(Role.role_name == 'Doctor').first()
    if not role:
        role = Role(role_name='Doctor')
        db.add(role); db.commit(); db.refresh(role)

    # Cleanup any previous test users and logs
    # First remove logs referencing any existing test users or containing the username
    existing_users = db.query(User).filter(func.lower(User.username) == 'audit_test').all()
    from app.models.user_flags import UserFlags
    for eu in existing_users:
        db.query(AuditLog).filter(AuditLog.user_id == eu.id).delete(synchronize_session=False)
        # Also remove any flags rows
        db.query(UserFlags).filter(UserFlags.user_id == eu.id).delete(synchronize_session=False)
    db.query(AuditLog).filter(AuditLog.action.like('%audit_test%')).delete(synchronize_session=False)
    db.query(User).filter(func.lower(User.username) == 'audit_test').delete(synchronize_session=False)
    db.commit()

    # Create the test user
    user = create_user(db, 'audit_test', 'mypw', role.id)

    # 1) Failed login
    r = client.post('/auth/login', json={'username':'audit_test','password':'wrong'})
    assert r.status_code == 401

    # 2) Successful login
    r = client.post('/auth/login', json={'username':'audit_test','password':'mypw'})
    assert r.status_code == 200

    # 3) Check audit logs contain both records
    # failed attempt is logged as action with username, success is logged with user_id
    failed_logged = db.query(AuditLog).filter(AuditLog.action.like('%LOGIN_FAILED: audit_test%')).first()
    assert failed_logged is not None
    success_logged = db.query(AuditLog).filter(AuditLog.user_id == user.id, AuditLog.action == 'LOGIN_SUCCESS').first()
    assert success_logged is not None

    # cleanup: delete audit logs referencing this user id or the username, then delete user
    from app.models.user_flags import UserFlags
    db.query(AuditLog).filter((AuditLog.action.like('%audit_test%')) | (AuditLog.user_id == user.id)).delete(synchronize_session=False)
    db.query(UserFlags).filter(UserFlags.user_id == user.id).delete(synchronize_session=False)
    db.query(User).filter(User.username == 'audit_test').delete(synchronize_session=False)
    db.commit()
    db.close()