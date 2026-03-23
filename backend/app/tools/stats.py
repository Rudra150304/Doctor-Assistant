# doctor-assistant/backend/app/tools/stats.py

from ..db import SessionLocal
from ..models import Appointment
from datetime import datetime, timedelta

def get_stats(query: str, doctor_id: int = None):
    db = SessionLocal()

    try:
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)

        q = query.lower()
        query_db = db.query(Appointment)

        if doctor_id:
            query_db = query_db.filter(Appointment.doctor_id == doctor_id)

        # 🔥 KEY FIX: detect time intent from full sentence
        if "yesterday" in q:
            count = query_db.filter(Appointment.date == yesterday).count()
            text = f"You had {count} patients yesterday."

        elif "today" in q:
            count = query_db.filter(Appointment.date == today).count()
            text = f"You have {count} appointments today."

        elif "tomorrow" in q:
            count = query_db.filter(Appointment.date == tomorrow).count()
            text = f"You have {count} appointments tomorrow."

        elif "total" in q:
            count = query_db.count()
            text = f"You have {count} total appointments."

        else:
            # 🔥 fallback: assume today if unclear
            count = query_db.filter(Appointment.date == today).count()
            text = f"You have {count} appointments today."

        return {
            "status": "success",
            "data": {
                "count": count,
                "text": text
            },
            "message": "Stats fetched successfully"
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message": str(e)
        }

    finally:
        db.close()
