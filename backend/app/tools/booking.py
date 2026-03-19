#doctor-assistant/backend/app/tools/booking.py
from ..logic import book_slot
from ..db import SessionLocal

def book_appointment(doctor_id: int, patient_name: str, date: str, time: str):
    db = SessionLocal()

    from datetime import datetime
    date_obj = datetime.strptime(date, "%Y-%m-%d").date()

    result = book_slot(db, doctor_id, patient_name, date_obj, time)

    db.close()

    return result
