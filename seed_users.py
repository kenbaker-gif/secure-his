from app.database import SessionLocal, engine, Base
from app.models.user import User, Role
from app.core.security import hash_password

# 1. Initialize tables (Integrity)
Base.metadata.create_all(bind=engine)

def seed_system():
    db = SessionLocal()
    try:
        # 2. Create Roles if they don't exist (Confidentiality)
        admin_role = db.query(Role).filter(Role.role_name == "Admin").first()
        if not admin_role:
            admin_role = Role(role_name="Admin")
            db.add(admin_role)
        
        doc_role = db.query(Role).filter(Role.role_name == "Doctor").first()
        if not doc_role:
            doc_role = Role(role_name="Doctor")
            db.add(doc_role)
        
        db.commit() # Save roles to get IDs

        # 3. Create an Admin User
        admin_user = db.query(User).filter(User.username == "admin_user").first()
        if not admin_user:
            new_admin = User(
                username="admin_user",
                hashed_password=hash_password("admin123"), # This will be hashed via Bcrypt
                role_id=admin_role.id
            )
            db.add(new_admin)

        # 4. Create a Doctor User
        doc_user = db.query(User).filter(User.username == "dr_smith").first()
        if not doc_user:
            new_doc = User(
                username="dr_smith",
                hashed_password=hash_password("doctor123"),
                role_id=doc_role.id
            )
            db.add(new_doc)

        db.commit()
        print("✅ Roles and Users created successfully!")
        print("Admin: username='admin_user', password='admin123'")
        print("Doctor: username='dr_smith', password='doctor123'")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_system()