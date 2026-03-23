# doctor-assistant/backend/app/tools/get_today_schedule.py

from ..db import SessionLocal
from ..models import Appointment
from datetime import datetime

def get_schedule(doctor_id: int, date: str = None):
    db = SessionLocal()

    try:
        if date:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        else:
            date_obj = datetime.now().date()

        appts = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.date == date_obj
        ).order_by(Appointment.time).all()

        if not appts:
            return {
                "status": "success",
                "data": {
                    "schedule": []
                },
                "message": f"No appointments scheduled for {date_obj}"
            }

        schedule = [
            f"{a.time.strftime('%H:%M')} - {a.patient_name}"
            for a in appts
        ]

        return {
            "status": "success",
            "data": {
                "schedule": schedule,
                "date": str(date_obj)
            },
            "message": "Schedule fetched successfully"
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message": str(e)
        }

    finally:
        db.close()
