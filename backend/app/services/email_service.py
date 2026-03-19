#doctor-assistant/backend/app/services/email_service.py
import os
import smtplib
from email.mime.text import MIMEText


def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "test@example.com"
    msg["To"] = to_email

    with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
        server.login(os.getenv("MAILTRAP_USER"), os.getenv("MAILTRAP_PASS"))
        server.send_message(msg)
