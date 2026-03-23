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
            "type": "object",
            "properties": {
                "doctor_id": {"type": "integer"},
                "date": {"type": "string"}
            },
            "required": ["doctor_id", "date"]
        }
    },
    {
        "name": "book_appointment",
        "description": "Book an appointment",
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_id": {"type": "integer"},
                "patient_name": {"type": "string"},
                "patient_email": {"type": "string"},
                "date": {"type": "string"},
                "time": {"type": "string"}
            },
            "required": ["doctor_id", "date", "time"]
        }
    },
    {
        "name": "cancel_appointment",
        "description": "Cancel an appointment",
        "parameters": {
            "type": "object",
            "properties": {
                "appointment_id": {"type": "integer"}
            },
            "required": ["appointment_id"]
        }
    },
    {
        "name": "get_stats",
        "description": "Get appointment statistics",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "doctor_id": {"type": "integer"}
            },
            "required": ["query"]
        }
    }
]


TOOL_MAP = {
    "check_availability": check_availability,
    "book_appointment": book_appointment,
    "cancel_appointment": cancel_appointment,
    "get_stats": get_stats,
    "get_schedule": get_schedule
}
