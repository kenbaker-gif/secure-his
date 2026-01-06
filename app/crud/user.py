from app.models.user import User
from app.core.security import hash_password

def create_user(db, username: str, password: str, role_id: int):
    """
    Create a new User with hashed password.
    Returns the User instance after committing to DB.
    """
    username = username.strip() if username else username
    hashed_pwd = hash_password(password)
    user = User(username=username, hashed_password=hashed_pwd, role_id=role_id)
    db.add(user)
    db.commit()
    db.refresh(user)  # important to get the DB-generated ID and relationship
    # Create default flags row
    try:
        from app.crud.user_flags import set_must_change
        set_must_change(db, user.id, False)
    except Exception:
        # Best-effort; do not fail user creation if flag creation fails
        pass
    return user
