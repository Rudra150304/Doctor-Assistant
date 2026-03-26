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
- ALWAYS use tools for actions
"""


def build_doctor_prompt(context):
    return f"""
You are assisting a DOCTOR.

Doctor ID: {context['doctor_id']}

GOALS:
- View schedule
- Get statistics

RULES:
- NEVER ask for doctor_id
- ALWAYS use tools
"""


# ---------------- AGENT ----------------
def run_agent(messages, context):
    tools = list_tools()
    today = datetime.now().strftime("%Y-%m-%d")

    # 🔥 DOCTOR MAPPING (CRITICAL FIX)
    doctor_map = """
Doctors:
- Dr. Ahuja → doctor_id = 1
- Dr. Sharma → doctor_id = 2
- Dr. Mehta → doctor_id = 3
- Dr. Gupta → doctor_id = 4
"""

    # ---------------- SYSTEM PROMPT ----------------
    system_prompt = f"""
You are an AI medical assistant.

Today's date is {today}.

-----------------------------------
DOCTOR MAPPING (IMPORTANT)
-----------------------------------
{doctor_map}

RULE:
- ALWAYS map doctor names to correct doctor_id
- NEVER assume doctor_id randomly
- If doctor not specified → ask user

-----------------------------------
CRITICAL RULE
-----------------------------------
If user asks anything about:
- availability
- schedule
- booking
- cancellation
- stats

YOU MUST CALL A TOOL.

-----------------------------------
DATE RULES
-----------------------------------
- "today" → {today}
- "tomorrow" → next date

-----------------------------------
RULES
-----------------------------------
- ALWAYS return valid JSON ONLY
- NO extra text outside JSON
- NEVER hallucinate

-----------------------------------
TOOLS
-----------------------------------
{json.dumps(tools)}

-----------------------------------
OUTPUT FORMAT
-----------------------------------
{{
  "tool": "tool_name",
  "args": {{}}
}}

OR

{{
  "final": "response"
}}
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

    llm_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": role_prompt},
        {"role": "user", "content": conversation}
    ]

    response_text = call_openrouter(llm_messages)

    print("🤖 RAW LLM:", response_text)

    if not response_text:
        return "LLM failed to respond."

    # ---------------- PARSE JSON ----------------
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
        tool_name = parsed["tool"]
        args = parsed.get("args", {})

        # 🔥 SAFETY: override doctor_id ONLY if doctor logged in
        if context.get("doctor_id"):
            args["doctor_id"] = context["doctor_id"]

        # Inject patient info ONLY when needed
        if tool_name == "book_appointment" and context.get("patient"):
            args["patient_name"] = context["patient"]["name"]
            args["patient_email"] = context["patient"]["email"]

        # Cancel fallback
        if tool_name == "cancel_appointment":
            if "appointment_id" not in args and context.get("last_appointment_id"):
                args["appointment_id"] = context["last_appointment_id"]

        parsed["args"] = args

        print("FINAL ARGS:", args)

        tool_result = execute_tool(parsed)

        print("📦 TOOL RESULT:", tool_result)

        # Store appointment ID
        if tool_name == "book_appointment" and tool_result.get("status") == "success":
            context["last_appointment_id"] = tool_result["data"].get("appointment_id")

        # ---------------- RESPONSE ----------------
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
