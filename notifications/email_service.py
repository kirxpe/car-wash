import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio
from config import SMTP_EMAIL, SMTP_PASS


async def notify_customer(user, order_id):
    await asyncio.sleep(0)  # Эмуляция асинхронной работы

    msg = MIMEMultipart()
    msg["From"] = SMTP_EMAIL
    msg["To"] = user.email
    msg["Subject"] = f"Заказ #{order_id} выполнен"

    body = f"Dear {user.first_name},\n\nВаш заказ с номером #{order_id} был выполнен"
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASS)
            text = msg.as_string()
            server.sendmail(SMTP_EMAIL, user.email, text)
            print(f"Email sent to {user.email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
