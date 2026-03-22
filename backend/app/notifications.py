#doctors-assistant/backend/app/notifications.py

from datetime import datetime

notifications = {}

def add_notification(doctor_id: int, message: str):
    notifications.setdefault(doctor_id, [])

    notifications[doctor_id].insert(0, {
        "text": message,
        "time": datetime.now().strftime("%H:%M")
    })
    notifications[doctor_id] = notifications[doctor_id][:10] 

def get_notifications(doctor_id: int):
    return {"notifications": notifications.get(doctor_id, [])}
