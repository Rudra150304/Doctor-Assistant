#doctor-assistant/backend/app/services/calendar_service.py
from ics import Calendar, Event
from datetime import datetime


def create_event(doctor_id, date, time):
    c = Calendar()
    e = Event()

    start = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")

    e.name = f"Doctor {doctor_id} Appointment"
    e.begin = start
    e.duration = {"hours": 1}

    c.events.add(e)

    file_path = f"appointment_{doctor_id}_{date}_{time}.ics"

    with open(file_path, "w") as f:
        f.writelines(c)

    return file_path
