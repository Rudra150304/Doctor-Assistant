# doctor-assistant/backend/app/tools/next_available_slot.py

from ..db import SessionLocal
from ..logic import get_available_slots
from datetime import datetime

def next_available_slot(doctor_id: int):
    db = SessionLocal()

    try:
        today = datetime.now().date()
        slots = get_available_slots(db, doctor_id, today)

        if not slots:
            return {"result": "No slots available today."}

        return {"result": f"Next available slot is {slots[0]}"}

    finally:
        db.close()
