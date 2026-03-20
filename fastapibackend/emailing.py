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


async def send_mail(messageschema: MessageSchema, usersdata: UserData = None):
    if usersdata is not None and usersdata.email_verified is False:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, {"error": "Email is not yet verified"}
        )
    await fastmail.send_message(messageschema)
