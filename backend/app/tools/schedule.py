# doctor-assistant/backend/app/tools/get_today_schedule.py

from ..db import SessionLocal
from ..models import Appointment
from datetime import datetime, time

def get_today_schedule(doctor_id: int):
    db = SessionLocal()

    try:
        today = datetime.now().date()

        appts = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.date == today
        ).order_by(Appointment.time).all()

        if not appts:
            return {"result": "No appointments scheduled for today."}

        schedule = [
            f"{a.time.strftime('%H:%M')} - {a.patient_name}"
            for a in appts
        ]

        return {"result": "Today's schedule:\n" + "\n".join(schedule)}

    finally:
        db.close()
