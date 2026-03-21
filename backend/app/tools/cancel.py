# doctor-assistant/backend/app/tools/cancel.py

from ..db import SessionLocal
from ..models import Appointment
from datetime import datetime, time

def cancel_appointment(doctor_id: int, date: str, time: str):
    db = SessionLocal()

    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        hour, minute = map(int, time.split(":"))

        appt = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.date == date_obj,
            Appointment.time == time(hour, minute)
        ).first()

        if not appt:
            return {"status": "failed", "reason": "No appointment found"}

        db.delete(appt)
        db.commit()

        return {"status": "success", "message": "Appointment cancelled"}

    except Exception as e:
        return {"status": "error", "error": str(e)}

    finally:
        db.close()
