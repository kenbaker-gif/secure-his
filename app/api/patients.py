from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.patient import Patient
from app.models.audit import AuditLog
import os

router = APIRouter(prefix="/patients", tags=["Patients"])

# Placeholder for dependency
def get_current_user(): 
    return {"id": 1, "role": "Doctor"} 

@router.get("/{patient_id}")
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Not found")
    return patient

@router.post("/{patient_id}/break-glass")
def break_glass(patient_id: int, reason: str, db: Session = Depends(get_db)):
    # Integrity: Log the emergency access
    log = AuditLog(user_id=1, action=f"BREAK-GLASS: {reason}", resource_id=str(patient_id))
    db.add(log)
    db.commit()
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    return {"warning": "Emergency Access Logged", "data": patient}