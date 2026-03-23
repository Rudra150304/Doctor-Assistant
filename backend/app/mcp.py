# doctor-assistant/backend/app/mcp.py

from typing import Dict
from .tools.registry import TOOL_MAP, TOOLS, get_tool_schema


def list_tools():
    return TOOLS


def validate_and_filter_args(tool_name: str, args: Dict):
    schema = get_tool_schema(tool_name)

    if not schema:
        return None, {"status": "error", "message": "Invalid tool"}

    properties = schema["parameters"]["properties"]
    required = schema["parameters"]["required"]

    # Filter only allowed args
    filtered = {k: v for k, v in args.items() if k in properties}

    # Check required
    missing = [k for k in required if k not in filtered]

    if missing:
        return None, {
            "status": "failed",
            "message": f"Missing required fields: {', '.join(missing)}"
        }

    return filtered, None


def call_tool(tool_name: str, args: Dict):
    if tool_name not in TOOL_MAP:
        return {
            "result": {
                "status": "error",
                "message": "Tool not found",
                "data": None
            }
        }

    # ---------------- VALIDATE ----------------
    args, error = validate_and_filter_args(tool_name, args)

    if error:
        return {"result": error}

    try:
        result = TOOL_MAP[tool_name](**args)

        # ---------------- ENFORCE FORMAT ----------------
        if not isinstance(result, dict):
            return {
                "result": {
                    "status": "error",
                    "message": "Invalid tool response",
                    "data": None
                }
            }

        if "status" not in result:
            return {
                "result": {
                    "status": "error",
                    "message": "Malformed tool response",
                    "data": result
                }
            }

        return {"result": result}

    except Exception as e:
        return {
            "result": {
                "status": "error",
                "message": str(e),
                "data": None
            }
        }
