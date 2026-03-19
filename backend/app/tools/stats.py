#doctor-assistant/backend/app/tools/stats.py
from ..db import SessionLocal
from ..models import Appointment
from datetime import datetime, timedelta


def get_stats(query: str):
    db = SessionLocal()

    try:
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        query = query.lower()

        if "yesterday" in query:
            count = db.query(Appointment).filter(
                Appointment.date == yesterday
            ).count()

            return {"result": f"{count} patients visited yesterday"}

        elif "today" in query:
            count = db.query(Appointment).filter(
                Appointment.date == today
            ).count()

            return {"result": f"{count} appointments today"}

        elif "tomorrow" in query:
            count = db.query(Appointment).filter(
                Appointment.date == tomorrow
            ).count()

            return {"result": f"{count} appointments tomorrow"}

        else:
            return {"result": "Query not understood"}

    finally:
        db.close()
