#doctor-assistant/backend/app/agent.py/logic.py
from .models import Appointment
from datetime import time

# Fixed slots (system-wide)
AVAILABLE_SLOTS = [
    "09:00",
    "10:00",
    "11:00",
    "12:00",
    "15:00",
    "16:00",
    "17:00"
]


def get_available_slots(db, doctor_id, date):
    booked = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == date
    ).all()

    # Convert booked times → "HH:MM"
    booked_times = {a.time.strftime("%H:%M") for a in booked}

    # Return only free slots
    return [slot for slot in AVAILABLE_SLOTS if slot not in booked_times]


def book_slot(db, doctor_id, patient_name, date, time_str):
    # Convert "HH:MM" → time object
    hour, minute = map(int, time_str.split(":"))
    time_obj = time(hour, minute)

    existing = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == date,
        Appointment.time == time_obj
    ).first()

    if existing:
        return {
            "status": "failed",
            "reason": "Slot already booked"
        }

    appt = Appointment(
        doctor_id=doctor_id,
        patient_name=patient_name,
        date=date,
        time=time_obj
    )

    db.add(appt)
    db.commit()

    return {
        "status": "success",
        "doctor_id": doctor_id,
        "date": str(date),
        "time": time_str
    }
