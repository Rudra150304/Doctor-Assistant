# doctor-assistant/backend/app/tools/cancel.py

from ..db import SessionLocal
from ..models import Appointment
from datetime import datetime, time
from ..services.email_service import send_email
from ..notifications import add_notification

def cancel_appointment(appointment_id: int):
    db = SessionLocal()

    try:
        appt = db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()

        if not appt:
            return {
                "status": "failed",
                "data": None,
                "message": "Appointment not found"
            }

        db.delete(appt)
        db.commit()

        send_email(
            to_email=appt.patient_email,
            subject="Appointment Cancelled",
            body=f"Your appointment at {appt.time.strftime('%H:%M')} has been cancelled."
        )

        add_notification(
            appt.doctor_id,
            f"❌ Appointment cancelled ({appt.patient_name})"
        )

        return {
            "status": "success",
            "data": {
                "appointment_id": appointment_id
            },
            "message": "Appointment cancelled successfully"
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message": str(e)
        }

    finally:
        db.close()
