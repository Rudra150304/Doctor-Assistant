#doctor-assistant/backend/app/tools/registry.py
from .availability import check_availability
from .booking import book_appointment
from .stats import get_stats

TOOLS = [
    {
        "name": "check_availability",
        "description": "Check doctor availability",
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
        "description": "Book appointment",
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
        "name": "get_stats",
        "description": "Get doctor statistics",
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
    "get_stats": get_stats
}
