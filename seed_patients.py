from app.database import SessionLocal, engine
from app.models.patient import Patient

def seed_patients():
    db = SessionLocal()
    try:
        # Check if we already have patients
        existing = db.query(Patient).first()
        if existing:
            print("✨ Patients already exist in Supabase. Connection is valid!")
            return

        # Sample Data (Confidential Medical Info)
        test_patients = [
            Patient(full_name="John Doe", medical_history="Hypertension, Type 2 Diabetes. Allergic to Penicillin."),
            Patient(full_name="Jane Smith", medical_history="No known allergies. Previous surgery: Appendectomy (2018)."),
            Patient(full_name="Baby Grace", medical_history="Asthmatic. Requires inhaler nearby at all times.")
        ]

        db.add_all(test_patients)
        db.commit()
        print("🚀 SUCCESS: Connection to Supabase is active. 3 Patient records added!")
    
    except Exception as e:
        print(f"❌ CONNECTION ERROR: Could not reach Supabase. Check your .env file.")
        print(f"Error Details: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_patients()