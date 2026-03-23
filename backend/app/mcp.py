# doctor-assistant/backend/app/mcp.py

from typing import Dict
from .tools.registry import TOOL_MAP
from .tools.registry import TOOLS


def list_tools():
    return TOOLS


def call_tool(tool_name: str, args: Dict):
    if tool_name not in TOOL_MAP:
        return {"result": {"status": "error", "message": "Tool not found"}}

    try:
        result = TOOL_MAP[tool_name](**args)
        return {"result": result}

    except Exception as e:
        return {"result": {"status": "error", "message": str(e)}}
