# doctor-assistant/backend/app/mcp.py

from typing import Dict
from .tools.registry import TOOL_MAP, TOOLS


def list_tools():
    return TOOLS


def execute_tool(tool_call: Dict):
    """
    MCP-style executor:
    Takes LLM output and routes it to correct tool
    """

    tool_name = tool_call.get("tool")
    args = tool_call.get("args", {})

    if tool_name not in TOOL_MAP:
        return {
            "status": "error",
            "data": None,
            "message": f"Tool '{tool_name}' not found"
        }

    try:
        result = TOOL_MAP[tool_name](**args)

        # Ensure standard response format
        if not isinstance(result, dict):
            return {
                "status": "success",
                "data": {"result": result},
                "message": "Executed"
            }

        return result

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message": str(e)
        }
