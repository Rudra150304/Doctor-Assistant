#doctor-assistant/backend/app/seed.py
from .db import SessionLocal
from .models import Doctor, Appointment
from datetime import date, time

def seed_doctors(db):
    if db.query(Doctor).count() == 0:
        db.add_all([
            Doctor(name="Dr. Ahuja", password="1234"),
            Doctor(name="Dr. Sharma", password="1234"),
            Doctor(name="Dr. Mehta", password="1234"),
            Doctor(name="Dr. Gupta", password="1234"),
        ])
        db.commit()

def seed_appointments(db):
    if db.query(Appointment).count() == 0:
        db.add_all([
            Appointment(
                doctor_id=1,
                patient_name="Rohit",
                date=date(2026, 3, 20),
                time=time(9, 0)
            ),
            Appointment(
                doctor_id=1,
                patient_name="Aman",
                date=date(2026, 3, 20),
                time=time(10, 0)
            ),
            Appointment(
                doctor_id=2,
                patient_name="Neha",
                date=date(2026, 3, 20),
                time=time(11, 0)
            ),
        ])
        db.commit()


def run_seed(reset=False):
    db = SessionLocal()

    if reset:
        db.query(Appointment).delete()
        db.query(Doctor).delete()
        db.commit()

    seed_doctors(db)
    seed_appointments(db)

    db.close()
