import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
load_dotenv()
def send_mail(receiver_mail:str,
             subject:str,
              body:str):
    sender_mail=os.getenv("sender_mail")
    sender_password=os.getenv("sender_password")
    if not sender_mail or not sender_password:
        raise ValueError("Email credentials are not configured")

    message=EmailMessage()

    message["From"]=sender_mail
    message["To"]=receiver_mail
    message["Subject"]=subject

    message.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com",465) as server:
        server.login(sender_mail,sender_password)
        server.send_message(message)
