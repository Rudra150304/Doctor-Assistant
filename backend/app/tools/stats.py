#doctor-assistant/backend/app/tools/stats.py
from ..db import SessionLocal
from ..models import Appointment
from datetime import datetime, timedelta

def get_stats(query: str, doctor_id: int = None):
    db = SessionLocal()

    try:
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)

        query_lower = query.lower()

        query_db = db.query(Appointment)

        # 👇 Filter by doctor
        if doctor_id:
            query_db = query_db.filter(Appointment.doctor_id == doctor_id)

        # 📋 Schedule overview (check this FIRST)
        if "schedule" in query_lower:
            appts = query_db.filter(Appointment.date == today).all()

            if not appts:
                return {"result": "No appointments scheduled for today."}

            schedule = [
                f"{a.time.strftime('%H:%M')} - {a.patient_name}"
                for a in appts
            ]

            return {
                "result": "Today's schedule:\n" + "\n".join(schedule)
            }

        # 📊 Yesterday
        if "yesterday" in query_lower:
            count = query_db.filter(Appointment.date == yesterday).count()
            return {"result": f"You had {count} patients yesterday."}

        # 📊 Today
        if "today" in query_lower:
            count = query_db.filter(Appointment.date == today).count()
            return {"result": f"You have {count} appointments today."}

        # 📊 Tomorrow
        if "tomorrow" in query_lower:
            count = query_db.filter(Appointment.date == tomorrow).count()
            return {"result": f"You have {count} appointments tomorrow."}

        # 📊 Total
        if "total" in query_lower:
            count = query_db.count()
            return {"result": f"You have {count} total appointments."}

        return {"result": "Sorry, I couldn't understand the request."}

    except Exception as e:
        print("❌ STATS ERROR:", e)
        return {"result": "Error fetching statistics."}

    finally:
        db.close()

