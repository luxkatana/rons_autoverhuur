from fastapi import HTTPException, status
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema
from authentication import UserData
from os import environ
from dotenv import load_dotenv

load_dotenv()
fastmail = FastMail(
    ConnectionConfig(
        MAIL_USERNAME=environ["MAIL_USERNAME"],
        MAIL_PASSWORD=environ["MAIL_PASSWORD"],
        MAIL_SERVER="smtp.gmail.com",
        MAIL_FROM=environ["MAIL_FROM"],
        MAIL_FROM_NAME="Team Razende Ron",
        MAIL_SSL_TLS=False,
        VALIDATE_CERTS=True,
        MAIL_PORT=587,
        MAIL_STARTTLS=True,
    )
)


async def send_mail(messageschema: MessageSchema, *args, **kwargs):
    await fastmail.send_message(messageschema)
