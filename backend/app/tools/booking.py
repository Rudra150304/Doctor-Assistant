# doctor-assistant/backend/app/tools/booking.py

from ..logic import book_slot, AVAILABLE_SLOTS
from ..db import SessionLocal
from ..services.calendar_service import create_event
from ..services.email_service import send_email
from datetime import datetime
from ..notifications import add_notification

def book_appointment(doctor_id: int, patient_name: str, patient_email: str, date: str, time: str):
    db = SessionLocal()

    try:
        if time not in AVAILABLE_SLOTS:
            return {"status": "failed", "reason": "Invalid time slot"}

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()

        result = book_slot(db, doctor_id, patient_name, patient_email, date_obj, time)

        if result.get("status") == "success":
            event_file = create_event(doctor_id, date, time)

            send_email(
                to_email= patient_email,
                subject="Appointment Confirmed",
                body=f"Dr. {doctor_id}, Date {date}, Time {time}"
            )

            add_notification(
                doctor_id,
                f"🆕 Appointment at {time} with {patient_name}"
            )

            return {
                "status": "success",
                "doctor_id": doctor_id,
                "appointment_id": result.get("appointment_id"),
                "date": date,
                "time": time,
                "calendar_file": event_file
            }

        return result

    except Exception as e:
        return {"status": "error", "error": str(e)}

    finally:
        db.close()
