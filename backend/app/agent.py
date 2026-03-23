# doctor-assistant/backend/app/agent.py

import json
import os
import re
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

from .mcp import call_tool, list_tools

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ---------------- SAFE JSON PARSER ----------------
def safe_parse_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"final": text.strip()}
    except Exception:
        print("⚠️ JSON PARSE FAILED:", text)
        return {"final": text.strip()}


# ---------------- OPENROUTER CALL ----------------
def call_openrouter(chat_text):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "temperature": 0,  # 🔥 critical for agents
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_conversation
                    }
                ]
            },
            timeout=20
        )

        print("🔍 STATUS:", response.status_code)

        if response.status_code != 200:
            print("❌ OpenRouter ERROR:", response.text)
            return None

        data = response.json()

        if "choices" in data:
            content = data["choices"][0]["message"]["content"]
            print("🤖 RAW LLM:", content)  # 🔥 debug visibility
            return content

        print("❌ Unexpected response:", data)
        return None

    except Exception as e:
        print("❌ OpenRouter EXCEPTION:", e)
        return None

# ---------------- ARG NORMALIZER ----------------
def normalize_args(tool_name, args):
    if tool_name == "book_appointment":
        if "slot" in args:
            args["time"] = args.pop("slot")

    if "doctor" in args:
        args["doctor_id"] = args.pop("doctor")

    return args


# ---------------- ARG FILTER (NEW 🔥) ----------------
def filter_args(tool_name, args, tools):
    """
    Keeps only allowed args based on tool schema.
    Prevents unexpected keyword crashes.
    """
    tool_schema = next((t for t in tools if t["name"] == tool_name), None)

    if not tool_schema:
        return {}

    allowed = tool_schema["parameters"]["properties"].keys()

    return {k: v for k, v in args.items() if k in allowed}

# ---------------- MAIN AGENT ----------------
def run_agent(session, doctor_id=None, role=None):

    messages = session["messages"]
    context = session.get("context", {})

    # ---------------- Patient Context ----------------
    patient_info = ""
    if "patient" in context:
        patient = context["patient"]
        patient_info = f"""
Patient:
Name: {patient.get("name")}
Email: {patient.get("email")}
"""

    # ---------------- Time ----------------
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    # ---------------- Tools ----------------
    tools = list_tools()
    tool_names = [t["name"] for t in tools]
    tool_list = "\n".join([f"- {name}" for name in tool_names])

    # ---------------- Prompt ----------------
    if role == "doctor":
        base_prompt = f"""
You are a doctor assistant.

Doctor ID = {doctor_id}

Rules:
- NEVER ask doctor
- Be concise
"""
    else:
        base_prompt = f"""
You are a patient assistant.

{patient_info}

Rules:
- NEVER ask name/email again
- Be helpful
"""

    system_prompt = f"""
{base_prompt}

Available tools:
{tool_list}

Doctor mapping:
Ahuja=1, Sharma=2, Mehta=3, Gupta=4

Today = {today}
Tomorrow = {tomorrow}

STRICT RULES:
- ALWAYS return valid JSON
- NEVER return text outside JSON
- ALWAYS include ALL required arguments for tools
- If user asks about stats → include "query"
- If user asks to book → include "date" and "time"
- Tool format: {{"tool": "...", "args": {{}}}}
- Final format: {{"final" : "..."}}
"""

    # ---------------- Build Chat ----------------
    chat_text = system_prompt + "\n\n"
    for msg in messages:
        chat_text += f"{msg['role']}: {msg['content']}\n"

    # ---------------- Call LLM ----------------
    text = call_openrouter(chat_text)

    if not text:
        return "AI unavailable. Try again."

    parsed = safe_parse_json(text)

    # ---------------- FINAL ----------------
    if "final" in parsed:
        return parsed["final"]

    tool_name = parsed.get("tool")
    args = parsed.get("args", {})

    # ---------------- AUTO-FILL MISSING ARGS ----------------

    if tool_name == "get_stats":
        if not args.get("query"):
            last_user_msg = next(
                (m["content"] for m in reversed(messages) if m["role"] == "user"),
                ""
            ).lower()
            # simple intent extraction
            if "today" in last_user_msg:
                args["query"] = "today"
            elif "yesterday" in last_user_msg:
                args["query"] = "yesterday"
            elif "tomorrow" in last_user_msg:
                args["query"] = "tomorrow"
            elif "total" in last_user_msg:
                args["query"] = "total"
            else:
                args["query"] = last_user_msg
    
    # ---------------- AUTO-FILL BOOKING ARGS ----------------
    if tool_name == "book_appointment":
        last_user_msg = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"),
            ""
        ).lower()
        # Extract time (HH:MM)
        time_match = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", last_user_msg)
        if time_match and not args.get("time"):
            args["time"] = time_match.group()

        # Extract date
        if "tomorrow" in last_user_msg and not args.get("date"):
            args["date"] = str(today + timedelta(days=1))

        elif "today" in last_user_msg and not args.get("date"):
            args["date"] = str(today)
    
    # ---------------- VALIDATION ----------------
    if not tool_name or tool_name not in tool_names:
        return "Sorry, I couldn't process that request."

    # ---------------- NORMALIZE ----------------
    args = normalize_args(tool_name, args)

    # ---------------- CONTEXT INJECTION ----------------
    if not args.get("doctor_id"):
        args["doctor_id"] = doctor_id or context.get("last_doctor_id")

    TOOLS_REQUIRING_DATE = ["check_availability", "book_appointment", "get_schedule"]

    if tool_name in TOOLS_REQUIRING_DATE:
        if not args.get("date"):
            args["date"] = context.get("availability", {}).get("date") or str(today)

    if tool_name == "book_appointment":
        patient = context.get("patient", {})
        args["patient_name"] = patient.get("name", "User")
        args["patient_email"] = patient.get("email", "test@mail.com")

    # ---------------- FILTER ARGS ----------------
    args = filter_args(tool_name, args, tools)

    print("🛠 TOOL:", tool_name, args)

    # ---------------- CALL TOOL ----------------
    tool_response = call_tool(tool_name, args)
    result = tool_response.get("result") if tool_response else None

    print("📦 RESULT:", result)

    # ---------------- FAIL SAFE ----------------
    if not isinstance(result, dict):
        return "Something went wrong. Please try again."

    status = result.get("status")

    if status == "error":
        return "Something went wrong. Please try again."

    # ---------------- STORE CONTEXT ----------------
    if tool_name == "check_availability" and status == "success":
        data = result.get("data") or {}
        context["availability"] = {
            "doctor_id": data.get("doctor_id"),
            "date": data.get("date"),
            "slots": data.get("available_slots", [])
        }
        context["last_doctor_id"] = data.get("doctor_id")

    if tool_name == "book_appointment" and status == "success":
        data = result.get("data") or {}
        context["last_appointment_id"] = data.get("appointment_id")
        return f"Appointment booked for {data.get('time')} on {data.get('date')}."

    # ---------------- RESPONSE HANDLING ----------------
    if status == "success":
        data = result.get("data") or {}
        # Availability
        if "available_slots" in data:
            slots = data["available_slots"]
            if not slots:
                return "No slots available."
            last_user_msg = next(
                (m["content"] for m in reversed(messages) if m["role"] == "user"),
                ""
            ).lower()
            if any(word in last_user_msg for word in ["next", "earliest"]):
                return f"Next available slot is {slots[0]}"

            return f"Available slots: {', '.join(slots)}"

        # Stats / generic text
        if "text" in data:
            return data["text"]

        # Schedule
        if "schedule" in data:
            if not data["schedule"]:
                return result["message"]

            return "\n".join(data["schedule"])

        return result.get("message", "Done.")

    if status == "failed":
        return result.get("message", "Action failed.")

    return "Task completed."
