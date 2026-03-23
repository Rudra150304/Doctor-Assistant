# doctor-assistant/backend/app/services/calendar_service.py

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/calendar"]


def create_event(doctor_id, date, time):
    try:
        creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

        if not creds_json:
            print("⚠️ Google Calendar not configured")
            return None

        creds_dict = json.loads(creds_json)

        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=SCOPES
        )

        service = build("calendar", "v3", credentials=creds)

        event = {
            "summary": f"Appointment with Doctor {doctor_id}",
            "start": {
                "dateTime": f"{date}T{time}:00",
                "timeZone": "Asia/Kolkata",
            },
            "end": {
                "dateTime": f"{date}T{time}:00",
                "timeZone": "Asia/Kolkata",
            },
        }

        event = service.events().insert(
            calendarId=os.getenv("CALENDAR_ID"),
            body=event
        ).execute()

        print("📅 Event created:", event.get("htmlLink"))

        return event.get("htmlLink")

    except Exception as e:
        print("❌ Calendar error:", e)
        return None
