# doctor-assistant/backend/app/services/email_service.py
import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_email(to_email: str, subject: str, body: str):
    try:
        SMTP_HOST = "sandbox.smtp.mailtrap.io"
        SMTP_PORT = 587

        SMTP_USER = os.getenv("MAILTRAP_USER")
        SMTP_PASS = os.getenv("MAILTRAP_PASS")

        if not SMTP_USER or not SMTP_PASS:
            print("⚠️ SMTP not configured, skipping email")
            return {"status": "skipped"}

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = "noreply@doctorassistant.com"
        msg["To"] = to_email

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()

        print("📧 Email sent via SMTP")

        return {"status": "sent"}

    except Exception as e:
        print("❌ Email error:", e)
        return {"status": "failed", "error": str(e)}
