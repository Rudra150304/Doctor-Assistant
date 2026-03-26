# doctor-assistant/backend/app/agent.py

import requests
import os
import json
import re
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
- NEVER include patient_name or email in tool args (handled automatically)
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
- NEVER include doctor_id in tool args (handled automatically)
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
CRITICAL RULE (NON-NEGOTIABLE)
-----------------------------------
If the user asks for:
- availability
- schedule
- statistics
- booking
- cancellation

YOU MUST call a tool.

DO NOT return "final".
DO NOT explain.
ONLY return a tool call.

-----------------------------------
GENERAL RULES
-----------------------------------
- ALWAYS return valid JSON
- NEVER return plain text outside JSON
- NEVER hallucinate data

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
ARGUMENT RULES
-----------------------------------
- DO NOT include doctor_id
- DO NOT include patient_name or email
- These are injected automatically

-----------------------------------
OUTPUT FORMAT (STRICT)
-----------------------------------

{{
  "tool": "tool_name",
  "args": {{ ... }}
}}

OR

{{
  "final": "response"
}}

-----------------------------------
FINAL INSTRUCTION
-----------------------------------
Be decisive. Always prefer tools.
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

    # ---------------- FIX JSON (IMPORTANT) ----------------
    try:
        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
        else:
            raise ValueError("No JSON found")

    except Exception:
        print("❌ Invalid JSON:", response_text)
        return "Sorry, I couldn't understand that."

    # ---------------- FINAL ----------------
    if "final" in parsed:
        return parsed["final"]

    # ---------------- TOOL EXECUTION ----------------
    if "tool" in parsed:
        args = parsed.get("args", {})

        # Inject doctor_id
        if context.get("doctor_id"):
            args["doctor_id"] = context["doctor_id"]

        # Inject patient info
        if context.get("patient"):
            args["patient_name"] = context["patient"]["name"]
            args["patient_email"] = context["patient"]["email"]

        parsed["args"] = args

        tool_result = execute_tool(parsed)

        print("📦 TOOL RESULT:", tool_result)

        # Store appointment
        if parsed["tool"] == "book_appointment" and tool_result.get("status") == "success":
            context["last_appointment_id"] = tool_result["data"].get("appointment_id")

        # ---------------- CLEAN OUTPUT ----------------
        if tool_result.get("status") == "success":
            data = tool_result.get("data", {})

            if "text" in data:
                return data["text"]

            if "available_slots" in data:
                return "Available slots: " + ", ".join(data["available_slots"])

            if "schedule" in data:
                if not data["schedule"]:
                    return "No appointments scheduled."
                return "\n".join(data["schedule"])

            return tool_result.get("message", "Done.")

        return tool_result.get("message", "Something went wrong.")

    return "Invalid response format."
