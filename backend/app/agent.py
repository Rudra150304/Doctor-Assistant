# doctor-assistant/backend/app/agent.py

import json
import os
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

from .mcp import call_tool, list_tools

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ---------------- SAFE JSON PARSER ----------------
def safe_parse_json(text):
    try:
        if "```" in text:
            text = text.split("```")[1]

        text = text.replace("json", "").strip()

        try:
            return json.loads(text)
        except:
            pass

        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1:
            return json.loads(text[start:end+1])

        return {"final": text}

    except Exception:
        print("⚠️ JSON PARSE FAILED. RAW:", text)
        return {"final": text}


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
                "model": "openrouter/free",
                "messages": [
                    {"role": "user", "content": chat_text}
                ]
            },
            timeout=30
        )

        data = response.json()
        print("🔍 RAW RESPONSE:", data)

        if "choices" in data:
            return data["choices"][0]["message"]["content"]

        return None

    except Exception as e:
        print("❌ OpenRouter ERROR:", e)
        return None


# ---------------- ARG NORMALIZER ----------------
def normalize_args(tool_name, args):
    if tool_name == "book_appointment":
        if "slot" in args:
            args["time"] = args.pop("slot")

    if "doctor" in args:
        args["doctor_id"] = args.pop("doctor")

    return args


# ---------------- MAIN AGENT ----------------
def run_agent(session, doctor_id=None, role=None, depth=0):

    # 🔥 HARD STOP
    if depth > 2:
        return "Something went wrong. Please try again."

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
    tool_list = "\n".join([f"- {t['name']}" for t in list_tools()])

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

Rules:
- Return ONLY JSON
- ONE object only
- Tool format: {{"tool": "...", "args": {{}}}}
- Final format: {{"final": "..."}}
- If task is completed → RETURN FINAL
"""

    # ---------------- Build Chat ----------------
    chat_text = system_prompt + "\n\n"
    for msg in messages:
        chat_text += f"{msg['role']}: {msg['content']}\n"

    # ---------------- Call LLM ----------------
    text = call_openrouter(chat_text)

    if not text:
        return "AI is busy. Try again."

    parsed = safe_parse_json(text)

    # ---------------- FINAL ----------------
    if "final" in parsed:
        return parsed["final"]

    tool_name = parsed.get("tool")
    args = parsed.get("args", {})

    # ---------------- Context Fix ----------------
    if not args.get("doctor_id"):
        args["doctor_id"] = doctor_id or context.get("last_doctor_id")

    if not args.get("date"):
        args["date"] = context.get("availability", {}).get("date") or str(today)

    if tool_name == "book_appointment":
        patient = context.get("patient", {})
        args["patient_name"] = patient.get("name", "User")
        args["patient_email"] = patient.get("email", "test@mail.com")

    args = normalize_args(tool_name, args)

    # ---------------- Call Tool ----------------
    result = call_tool(tool_name, args).get("result")

    # ---------------- STORE CONTEXT ----------------
    if tool_name == "check_availability":
        context["availability"] = {
            "doctor_id": args["doctor_id"],
            "date": args["date"],
            "slots": result.get("available_slots", [])
        }
        context["last_doctor_id"] = args["doctor_id"]

    if tool_name == "book_appointment" and result.get("status") == "success":
        context["last_appointment_id"] = result.get("appointment_id")

        # 🔥 FORCE FINAL AFTER BOOKING
        return f"Appointment booked for {args['time']} on {args['date']}."

    # ---------------- Append ----------------
    messages.append({"role": "tool", "content": json.dumps(result)})

    # 🔥 Prevent infinite loop
    if depth >= 2:
        return "Task completed."

    return run_agent(session, doctor_id, role, depth + 1)
