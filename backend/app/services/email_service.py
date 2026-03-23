# doctor-assistant/backend/app/services/email_service.py

import requests
import os


SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")  # your verified sender


def send_email(to_email: str, subject: str, body: str):
    try:
        if not SENDGRID_API_KEY or not FROM_EMAIL:
            print("⚠️ SendGrid not configured")
            return {"status": "skipped"}

        url = "https://api.sendgrid.com/v3/mail/send"

        headers = {
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "personalizations": [
                {
                    "to": [{"email": to_email}]
                }
            ],
            "from": {"email": FROM_EMAIL},
            "subject": subject,
            "content": [
                {
                    "type": "text/plain",
                    "value": body
                }
            ]
        }

        response = requests.post(url, headers=headers, json=data)

        print("📧 SENDGRID:", response.status_code, response.text)

        if response.status_code == 202:
            return {"status": "sent"}

        return {"status": "failed", "error": response.text}

    except Exception as e:
        print("❌ Email error:", e)
        return {"status": "failed", "error": str(e)}
