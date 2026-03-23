# doctor-assistant/backend/app/agent.py

import json
from .mcp import list_tools, execute_tool
from .llm import call_openrouter  # your existing function


def run_agent(messages, context):
    """
    MCP-style agent:
    - LLM decides tool
    - Agent only routes
    - No manual logic overrides
    """

    tools = list_tools()

    system_prompt = f"""
You are a medical assistant AI.

You have access to tools.

STRICT RULES:
- ALWAYS return valid JSON
- Use tools when needed
- NEVER hallucinate results
- If action needed → return:
  {{"tool": "tool_name", "args": {{}}}}
- If final answer → return:
  {{"final": "response"}}

TOOLS:
{json.dumps(tools)}
"""

    # Build conversation
    conversation = ""
    for msg in messages:
        conversation += f"{msg['role']}: {msg['content']}\n"

    llm_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": conversation}
    ]

    # Call LLM
    response_text = call_openrouter(llm_messages)

    print("🤖 RAW LLM:", response_text)

    try:
        parsed = json.loads(response_text)
    except Exception:
        return "Sorry, I couldn't understand that."

    # 🔥 FINAL RESPONSE
    if "final" in parsed:
        return parsed["final"]

    # 🔥 TOOL EXECUTION (MCP)
    if "tool" in parsed:
        tool_result = execute_tool(parsed)

        print("📦 TOOL RESULT:", tool_result)

        # Store context safely
        if parsed["tool"] == "book_appointment" and tool_result.get("status") == "success":
            context["last_appointment_id"] = tool_result["data"].get("appointment_id")

        # Return human-readable response
        if tool_result.get("status") == "success":
            if tool_result.get("data") and tool_result["data"].get("text"):
                return tool_result["data"]["text"]

            return tool_result.get("message", "Action completed.")

        return tool_result.get("message", "Something went wrong.")

    return "Invalid response format."
