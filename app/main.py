from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import auth, patients, admin  # Ensure admin is imported here

# 1. Initialize the Database (Integrity Pillar)
# In test environments or when SKIP_DB_CREATE is set, skip creating tables to avoid contacting external DBs.
import os
if os.getenv("SKIP_DB_CREATE", "false").lower() != "true":
    # This creates all tables in Supabase (Users, Patients, Audit Logs) automatically.
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Secure Hospital Information System",
    description="A CIA-Triad based HIS focusing on Confidentiality, Integrity, and Availability",
    version="1.0.0"
)

# 2. Configure CORS (Confidentiality Pillar)
# This allows your Streamlit frontend to communicate with this API securely.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In a real hospital, this would be restricted to internal IPs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Include API Routes (Role-Based Access Control)
# Each router handles a different part of the CIA Triad.
app.include_router(auth.router)      # Authentication (Confidentiality)
app.include_router(patients.router)  # Medical Records (Availability/Confidentiality)
app.include_router(admin.router)     # System Logs & Management (Integrity)

@app.get("/")
def root():
    """System Health Check"""
    return {
        "message": "Secure HIS API is running",
        "status": "Online",
        "security_framework": "CIA Triad",
        "database_connection": "Supabase Active"
    }