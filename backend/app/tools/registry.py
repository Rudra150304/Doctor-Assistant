from .availability import check_availability
from .booking import book_appointment
from .stats import get_stats
from .cancel import cancel_appointment
from .schedule import get_today_schedule
from .next_available_slot import next_available_slot

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
        "description": "Book an appointment for a patient with a doctor",
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_id": {"type": "integer"},
                "patient_name": {"type": "string"},
                "date": {"type": "string"},
                "time": {"type": "string"}
            },
            "required": ["doctor_id", "patient_name", "date", "time"]
        }
    },
    {
        "name": "next_available_slot",
        "description": "Get next available slot for today",
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_id": {"type": "integer"}
            },
            "required": ["doctor_id"]
        }
    },
    {
        "name": "cancel_appointment",
        "description": "Cancel an existing appointment for a doctor",
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_id": {"type": "integer"},
                "date": {"type": "string"},
                "time": {"type": "string"}
            },
            "required": ["doctor_id", "date", "time"]
        }
    },
    {
        "name": "get_today_schedule",
        "description": "Get full list of today's appointments for a doctor",
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_id": {"type": "integer"}
            },
            "required": ["doctor_id"]
        }
    },
    {
        "name": "get_stats",
        "description": "Get appointment statistics like today, tomorrow, total",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    }
]


TOOL_MAP = {
    "check_availability": check_availability,
    "book_appointment": book_appointment,
    "cancel_appointment": cancel_appointment,
    "get_today_schedule": get_today_schedule,
    "next_available_slot": next_available_slot,
    "get_stats": get_stats
}
