import json
import os
from datetime import datetime, timedelta

import google.generativeai as genai
from dotenv import load_dotenv

from .tools.registry import TOOL_MAP
from .services.calendar_service import create_event
from .services.email_service import send_email

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

def run_agent(messages, doctor_id=None, depth=0):
    if depth > 5:
        return "Error: Too many tool calls"

    import json
    from datetime import datetime, timedelta

    # 🔥 Dynamic dates
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    day_after = today + timedelta(days=2)

    system_prompt = f"""
You are a strict medical assistant AI.

You MUST decide actions using tools.
DO NOT ask follow-up questions.

Doctor mapping:
Dr. Ahuja = 1
Dr. Sharma = 2
Dr. Mehta = 3
Dr. Gupta = 4

Time rules:
morning = 09:00
afternoon = 15:00
evening = 17:00

Date rules:
today = {today}
tomorrow = {tomorrow}
day after tomorrow = {day_after}

---

If user wants to check availability → return JSON:
{{
  "tool": "check_availability",
  "args": {{
    "doctor_id": 2,
    "date": "{tomorrow}"
  }}
}}

If user wants to book → return JSON:
{{
  "tool": "book_appointment",
  "args": {{
    "doctor_id": 2,
    "patient_name": "User",
    "date": "{tomorrow}",
    "time": "17:00"
  }}
}}

If user asks about statistics or reports, use "get_stats" tool.
For get_stats, ALWAYS include "query" argument exactly from user message.

---

DO NOT explain.
DO NOT change doctor_id once selected.
ONLY output JSON.
"""

    # Build prompt
    chat_text = system_prompt + "\n\n"
    for msg in messages:
        chat_text += f"{msg['role']}: {msg['content']}\n"

    response = model.generate_content(chat_text)
    text = getattr(response, "text", None)

    if not text:
        return "⚠️ Could not generate response."

    text = text.strip()
    print("MODEL RAW:", text)

    try:
        # Clean markdown JSON
        if "```" in text:
            parts = text.split("```")
            if len(parts) >= 2:
                text = parts[1].replace("json", "").strip()

        data = json.loads(text)

        tool_name = data.get("tool")
        args = data.get("args", {})

        # Inject doctor context
        if tool_name == "get_stats" and doctor_id:
            args["doctor_id"] = doctor_id

        if tool_name not in TOOL_MAP:
            print("⚠️ Unknown tool:", tool_name)
            return "Sorry, I couldn't process that request."

        print("TOOL CALLED:", tool_name, args)

        try:
            result = TOOL_MAP[tool_name](**args)
        except Exception as e:
            print("❌ TOOL ERROR:", e)
            return "Something went wrong while processing your request."

        print("RESULT:", result)

        messages.append({"role": "assistant", "content": text})
        messages.append({"role": "tool", "content": json.dumps(result)})

        # ✅ SUCCESS FLOW
        if isinstance(result, dict) and result.get("status") == "success":
            event_file = create_event(
                doctor_id=args["doctor_id"],
                date=args["date"],
                time=args["time"]
            )

            print("📅 Calendar created:", event_file)

            send_email(
                "test@mail.com",
                "Appointment Confirmed",
                "Your appointment has been successfully booked."
            )

            print("📧 Email sent")

            return "✅ Appointment booked successfully! A confirmation email has been sent."

        # ❌ FAILURE FLOW
        if isinstance(result, dict) and result.get("status") == "failed":
            print("RETRYING: checking availability...")

            slots = TOOL_MAP["check_availability"](
                doctor_id=args["doctor_id"],
                date=args["date"]
            )

            return (
                f"❌ Slot already booked.\n"
                f"Available slots: {', '.join(slots['available_slots'])}"
            )

        # 📊 AVAILABILITY FLOW
        if isinstance(result, dict) and "available_slots" in result:
            slots = result["available_slots"]
            user_msg = messages[-1]["content"].lower()

            if "latest" in user_msg:
                return f"Latest available slot: {slots[-1]}"

            return f"Available slots: {', '.join(slots)}"

        # 📊 STATS FLOW
        if isinstance(result, dict) and "result" in result:
            return result["result"]

    except Exception as e:
        print("JSON PARSE FAILED:", e)

    return text

