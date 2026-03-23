# doctor-assistant/backend/app/tools/registry.py

from .availability import check_availability
from .booking import book_appointment
from .stats import get_stats
from .cancel import cancel_appointment
from .schedule import get_schedule


TOOLS = [
    {
        "name": "check_availability",
        "description": "Check available time slots for a doctor on a given date",
        "parameters": {
            "properties": {
                "doctor_id": int,
                "date": str
            },
            "required": ["doctor_id", "date"]
        }
    },
    {
        "name": "book_appointment",
        "description": "Book an appointment",
        "parameters": {
            "properties": {
                "doctor_id": int,
                "patient_name": str,
                "patient_email": str,
                "date": str,
                "time": str
            },
            "required": ["doctor_id", "patient_name", "patient_email", "date", "time"]
        }
    },
    {
        "name": "cancel_appointment",
        "description": "Cancel appointment",
        "parameters": {
            "properties": {
                "appointment_id": int
            },
            "required": ["appointment_id"]
        }
    },
    {
        "name": "get_schedule",
        "description": "Get doctor's schedule",
        "parameters": {
            "properties": {
                "doctor_id": int,
                "date": str
            },
            "required": ["doctor_id"]
        }
    },
    {
        "name": "get_stats",
        "description": "Get appointment statistics",
        "parameters": {
            "properties": {
                "query": str
            },
            "required": ["query"]
        }
    }
]


TOOL_MAP = {
    "check_availability": check_availability,
    "book_appointment": book_appointment,
    "cancel_appointment": cancel_appointment,
    "get_schedule": get_schedule,
    "get_stats": get_stats
}


# ---------------- HELPERS ----------------

def get_tool_schema(tool_name):
    return next((t for t in TOOLS if t["name"] == tool_name), None)
