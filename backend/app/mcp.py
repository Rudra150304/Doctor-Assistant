#doctor-assistant/backend/app/mcp.py
from pydantic import BaseModel
from typing import Dict


class ToolSchema(BaseModel):
    name: str
    description: str
    input_schema: Dict


TOOLS_MCP = [
    ToolSchema(
        name="check_availability",
        description="Check available time slots for a doctor",
        input_schema={
            "doctor_id": "integer",
            "date": "string"
        }
    ),
    ToolSchema(
        name="book_appointment",
        description="Book an appointment",
        input_schema={
            "doctor_id": "integer",
            "patient_name": "string",
            "date": "string",
            "time": "string"
        }
    ),
    ToolSchema(
        name="get_stats",
        description="Get doctor stats",
        input_schema={"query": "string"}
    ),
]
