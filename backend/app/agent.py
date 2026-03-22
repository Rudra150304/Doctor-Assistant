# doctor-assistant/backend/app/agent.py

import json
import os
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

from .mcp import call_tool, list_tools

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def run_agent(session, doctor_id=None, role=None, depth=0):
    if depth > 5:
        return "Request too complex. Please try again."

    messages = session["messages"]
    context = session.get("context", {})

    # ---------------- Patient Context ----------------
    patient_info = ""
    if "patient" in context:
        patient = context["patient"]
        patient_info = f"""
Current patient:
Name: {patient.get("name")}
Email: {patient.get("email")}
"""

    # ---------------- Time ----------------
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    day_after = today + timedelta(days=2)

    # ---------------- Tools ----------------
    tool_list = "\n".join(
        [f"- {t['name']}({', '.join(t['input_schema'].keys())})" for t in list_tools()]
    )

    # ---------------- Role Prompt ----------------
    if role == "doctor":
        base_prompt = f"""
You are an AI assistant for doctors.

Doctor ID: {doctor_id}

You help with:
- viewing today's schedule
- checking stats
- finding next available slot
- cancelling appointments

Rules:
- NEVER ask which doctor
- ALWAYS use doctor_id = {doctor_id}
- Be concise
"""
    else:
        base_prompt = f"""
You are an AI assistant for patients.

{patient_info}

You help with:
- checking doctor availability
- booking appointments
- cancelling appointments using appointment_id

Rules:
- NEVER ask name/email again if already provided
- ALWAYS check availability before booking
- Be friendly
"""

    # ---------------- System Prompt ----------------
    system_prompt = f"""
{base_prompt}

Available tools:
{tool_list}

Doctor mapping:
Dr. Ahuja = 1
Dr. Sharma = 2
Dr. Mehta = 3
Dr. Gupta = 4

Dates:
today = {today}
tomorrow = {tomorrow}
day after tomorrow = {day_after}

Available slots:
["09:00","10:00","11:00","12:00","15:00","16:00","17:00"]

Rules:
1. You MUST return valid JSON only. No explanations.
2. Use tools when needed
3. ONE tool call only
4. Tool format:
   {{ "tool": "name", "args": {{...}} }}
5. Final format:
   {{ "final": "message" }}
"""

    # ---------------- Build Chat Context ----------------
    chat_text = system_prompt + "\n\n"

    for msg in messages:
        chat_text += f"{msg['role']}: {msg['content']}\n"

    # ---------------- Call LLM ----------------
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "z-ai/glm-4.5-air:free",
                "messages": [
                    {
                        "role": "user",
                        "content": chat_text   # ✅ FULL CONTEXT HERE
                    }
                ]
            }
        )

        data = response.json()

        if "choices" not in data:
            print("❌ API ERROR:", data)
            return "AI service error."

        text = data["choices"][0]["message"]["content"].strip()

        if not text:
            return "Empty response from AI."

    except Exception as e:
        print("❌ LLM ERROR:", e)
        return "AI service temporarily unavailable."

    # ---------------- Parse JSON ----------------
    try:
        if "```" in text:
            parts = text.split("```")
            if len(parts) > 1:
                text = parts[1]

        text = text.replace("json", "").strip()

        parsed = json.loads(text)

        # ---------------- Final Response ----------------
        if "final" in parsed:
            return parsed["final"]

        tool_name = parsed.get("tool")
        args = parsed.get("args", {})

        # ---------------- Inject doctor_id ----------------
        if doctor_id:
            args["doctor_id"] = doctor_id

        # ---------------- Inject patient ----------------
        if tool_name == "book_appointment":
            patient = context.get("patient", {})
            args["patient_name"] = patient.get("name", "Unknown")
            args["patient_email"] = patient.get("email", "test@mail.com")

        # ---------------- Inject appointment_id ----------------
        if tool_name == "cancel_appointment" and "appointment_id" not in args:
            last_id = context.get("last_appointment_id")
            if last_id:
                args["appointment_id"] = last_id

        # ---------------- Safety ----------------
        if role == "doctor" and tool_name == "book_appointment":
            return "Doctors cannot book appointments."

        if tool_name == "book_appointment" and "availability" not in context:
            return "Please check availability first."

        # ---------------- Call Tool ----------------
        result = call_tool(tool_name, args).get("result")

        # ---------------- Store appointment ----------------
        session.setdefault("context", {})

        if tool_name == "book_appointment" and result.get("status") == "success":
            session["context"]["last_appointment_id"] = result.get("appointment_id")

        if tool_name == "check_availability":
            session["context"]["availability"] = {
                "doctor_id": args.get("doctor_id"),
                "date": args.get("date"),
                "slots": result.get("available_slots", [])
            }

        # ---------------- Append Messages ----------------
        messages.append({"role": "assistant", "content": json.dumps(parsed)})
        messages.append({"role": "tool", "content": json.dumps(result)})

        return run_agent(session, doctor_id, role, depth + 1)

    except Exception as e:
        print("❌ PARSE ERROR:", e)
        print("RAW:", text)
        return "Something went wrong."
