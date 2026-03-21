# doctor-assistant/backend/app/mcp.py

from typing import Dict
from .tools.registry import TOOL_MAP


def list_tools():
    return [
        {
            "name": name,
            "input_schema": {}
        }
        for name in TOOL_MAP.keys()
    ]


def call_tool(tool_name: str, args: Dict):
    if tool_name not in TOOL_MAP:
        return {"result": {"status": "error", "message": "Tool not found"}}

    try:
        result = TOOL_MAP[tool_name](**args)
        return {"result": result}

    except Exception as e:
        return {"result": {"status": "error", "message": str(e)}}
