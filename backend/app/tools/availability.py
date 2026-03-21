# doctor-assistant/backend/app/tools/availability.py

from ..logic import get_available_slots
from ..db import SessionLocal
from datetime import datetime


def check_availability(doctor_id: int, date: str):
    db = SessionLocal()

    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        slots = get_available_slots(db, doctor_id, date_obj)

        return {
            "doctor_id": doctor_id,
            "date": date,
            "available_slots": slots
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        db.close()
