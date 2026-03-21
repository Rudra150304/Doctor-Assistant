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

        if any(x in q for x in ["yesterday", "last day"]):
            count = query_db.filter(Appointment.date == yesterday).count()
            return {"result": f"You had {count} patients yesterday."}

        if any(x in q for x in ["today", "now"]):
            count = query_db.filter(Appointment.date == today).count()
            return {"result": f"You have {count} appointments today."}

        if "tomorrow" in q:
            count = query_db.filter(Appointment.date == tomorrow).count()
            return {"result": f"You have {count} appointments tomorrow."}

        if "total" in q:
            count = query_db.count()
            return {"result": f"You have {count} total appointments."}

        return {"result": "Query not understood."}

    except Exception:
        return {"result": "Error fetching statistics."}

    finally:
        db.close()
