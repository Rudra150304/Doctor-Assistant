#doctor-assistant/backend/app/tools/availability.py
from ..logic import get_available_slots
from ..db import SessionLocal

def check_availability(doctor_id: int, date: str):
    db = SessionLocal()

    from datetime import datetime
    date_obj = datetime.strptime(date, "%Y-%m-%d").date()

    slots = get_available_slots(db, doctor_id, date_obj)

    db.close()

    return {
        "doctor_id": doctor_id,
        "date": date,
        "available_slots": slots
    }
