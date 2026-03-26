# doctor-assistant/backend/app/agent.py

import requests
import os
import json
from datetime import datetime

from .mcp import list_tools, execute_tool

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ---------------- LLM CALL ----------------
def call_openrouter(messages):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": messages
            },
            timeout=20
        )

        if response.status_code != 200:
            print("❌ OpenRouter ERROR:", response.text)
            return None

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("❌ OpenRouter EXCEPTION:", e)
        return None


# ---------------- ROLE PROMPTS ----------------
def build_patient_prompt(context):
    return f"""
You are assisting a PATIENT.

Patient details:
- Name: {context['patient']['name']}
- Email: {context['patient']['email']}

GOALS:
- Check availability
- Book appointment
- Cancel appointment

RULES:
- NEVER ask for patient details
- Use tools for all actions
"""


def build_doctor_prompt(context):
    return f"""
You are assisting a DOCTOR.

Doctor details:
- Doctor ID: {context['doctor_id']}

GOALS:
- View schedule
- Get statistics

RULES:
- NEVER ask for doctor_id
- Use tools for all queries
"""


# ---------------- AGENT ----------------
def run_agent(messages, context):
    tools = list_tools()
    today = datetime.now().strftime("%Y-%m-%d")

    # ---------------- SYSTEM PROMPT ----------------
    system_prompt = f"""
You are an AI medical assistant.

Today's date is {today}.

-----------------------------------
YOUR JOB
-----------------------------------
- Understand user intent
- Decide if a tool is needed
- Call tools when required
- Return final answers when no tool needed

-----------------------------------
RULES
-----------------------------------
- ALWAYS return valid JSON
- NEVER return plain text outside JSON
- NEVER hallucinate data
- ALWAYS use tools for real-world data

-----------------------------------
DATE RULES
-----------------------------------
- "today" → {today}
- "tomorrow" → next date
- Always use YYYY-MM-DD

-----------------------------------
TOOLS
-----------------------------------
{json.dumps(tools)}

-----------------------------------
WHEN TO USE TOOLS
-----------------------------------
availability → check_availability  
booking → book_appointment  
cancel → cancel_appointment  
schedule → get_schedule  
stats → get_stats  

-----------------------------------
OUTPUT FORMAT (STRICT)
-----------------------------------

Tool call:
{{
  "tool": "tool_name",
  "args": {{ ... }}
}}

Final response:
{{
  "final": "response"
}}

-----------------------------------
IMPORTANT
-----------------------------------
- DO NOT ask for missing IDs
- DO NOT invent data
- ALWAYS prefer tool usage
- DO NOT say "I cannot"

-----------------------------------
FINAL INSTRUCTION
-----------------------------------
Be decisive. Use tools.
"""

    # ---------------- ROLE PROMPT ----------------
    role_prompt = ""

    if context.get("doctor_id"):
        role_prompt = build_doctor_prompt(context)

    elif context.get("patient"):
        role_prompt = build_patient_prompt(context)

    # ---------------- BUILD CONVERSATION ----------------
    conversation = ""

    for msg in messages:
        conversation += f"{msg['role']}: {msg['content']}\n"

    # ---------------- LLM CALL ----------------
    llm_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": role_prompt},
        {"role": "user", "content": conversation}
    ]

    response_text = call_openrouter(llm_messages)

    print("🤖 RAW LLM:", response_text)

    if not response_text:
        return "LLM failed to respond."

    # ---------------- PARSE RESPONSE ----------------
    try:
        parsed = json.loads(response_text)
    except Exception:
        print("❌ Invalid JSON:", response_text)
        return "Sorry, I couldn't understand that."

    # ---------------- FINAL ----------------
    if "final" in parsed:
        return parsed["final"]

    # ---------------- TOOL EXECUTION ----------------
    if "tool" in parsed:
        args = parsed.get("args", {})

        # Inject doctor_id automatically
        if context.get("doctor_id"):
            args["doctor_id"] = context["doctor_id"]

        # Inject patient automatically
        if context.get("patient"):
            args["patient_name"] = context["patient"]["name"]
            args["patient_email"] = context["patient"]["email"]

        parsed["args"] = args

        tool_result = execute_tool(parsed)

        print("📦 TOOL RESULT:", tool_result)

        # Save appointment ID
        if parsed["tool"] == "book_appointment" and tool_result.get("status") == "success":
            context["last_appointment_id"] = tool_result["data"].get("appointment_id")

        # ---------------- CLEAN OUTPUT ----------------
        if tool_result.get("status") == "success":
            data = tool_result.get("data", {})

            # stats
            if "text" in data:
                return data["text"]

            # availability
            if "available_slots" in data:
                return "Available slots: " + ", ".join(data["available_slots"])

            # schedule
            if "schedule" in data:
                if not data["schedule"]:
                    return "No appointments scheduled."
                return "\n".join(data["schedule"])

            return tool_result.get("message", "Done.")

        return tool_result.get("message", "Something went wrong.")

    return "Invalid response format."
