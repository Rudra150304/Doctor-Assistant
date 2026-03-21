# doctor-assistant/backend/app/auth.py

from fastapi import APIRouter
from pydantic import BaseModel
from .db import SessionLocal
from .models import Doctor

router = APIRouter()


class DoctorLogin(BaseModel):
    doctor_id: int
    password: str


class PatientLogin(BaseModel):
    name: str
    email: str


@router.post("/login/doctor")
def doctor_login(data: DoctorLogin):
    db = SessionLocal()

    doctor = db.query(Doctor).filter(Doctor.id == data.doctor_id).first()

    if not doctor or doctor.password != data.password:
        return {"success": False, "message": "Invalid credentials"}

    return {
        "success": True,
        "doctor_id": doctor.id,
        "name": doctor.name
    }


@router.post("/login/patient")
def patient_login(data: PatientLogin):
    return {
        "success": True,
        "name": data.name,
        "email": data.email
    }
