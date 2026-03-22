# doctor-assistant/backend/app/services/email_service.py

import mailtrap as mt
import os
from dotenv import load_dotenv

load_dotenv()


def send_email(to_email: str, subject: str, body: str):
    try:
        MAILTRAP_TOKEN = os.getenv("MAILTRAP_TOKEN")
        MAILTRAP_INBOX_ID = os.getenv("MAILTRAP_INBOX_ID")

        if not MAILTRAP_TOKEN or not MAILTRAP_INBOX_ID:
            raise ValueError("Mailtrap env variables not set")

        MAILTRAP_INBOX_ID = int(MAILTRAP_INBOX_ID)

        mail = mt.Mail(
            sender=mt.Address(
                email="noreply@doctorassistant.com",
                name="Doctor Assistant"
            ),
            to=[mt.Address(email=to_email)],
            subject=subject,
            text=body,
            category="Appointment"
        )

        client = mt.MailtrapClient(
            token=MAILTRAP_TOKEN,
            sandbox=True,
            inbox_id=MAILTRAP_INBOX_ID
        )

        response = client.send(mail)

        print("📧 Mailtrap response:", response)

        return {"status": "sent"}

    except Exception as e:
        print("❌ Email error:", e)
        return {"status": "failed", "error": str(e)}
