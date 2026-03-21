from fastapi import APIRouter, BackgroundTasks, Header, Request
from fastapi_mail import MessageSchema, MessageType
import stripe
from bson import ObjectId
from emailing import send_mail
from db import usersdata, authentication
from dotenv import load_dotenv
from os import environ

load_dotenv()
stripe.api_key = environ["STRIPE_SECRET_KEY"]
webhook_secret = environ["STRIPE_WEBHOOK_SECRET"]


StripeWebhooksRouter = APIRouter()


@StripeWebhooksRouter.post("/webhook")
async def webhook_endpoint(
    request: Request, bg: BackgroundTasks, stripe_signature: str = Header(None)
):
    data = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload=data, sig_header=stripe_signature, secret=webhook_secret
        )
    except Exception as e:
        return {"error": str(e)}

    event_type = event["type"]
    print(event_type)
    if event_type in [
        "identity.verification_session.requires_input",
        "identity.verification_session.verified",
    ]:  # TODO: If, and only if this project will be used in production, then this code must be different. In testing mode, stripe does not verify the identity, so we just assuming it went through
        session_id: str = event["data"]["object"]["id"]
        verificationsession = await stripe.identity.VerificationSession.retrieve_async(
            session_id
        )

        usr_id = verificationsession.metadata["user_id"]
        authentication_data = await authentication.find_one({"_id": ObjectId(usr_id)})
        email = authentication_data["email"]
        bg.add_task(
            send_mail,
            MessageSchema(
                recipients=[email],
                subject="Rijebwijs geverifieerd, nu alleen nog leeftijd-verificatie",
                body="Hallo, rijbewijs is nu ook geverifieerd, nu alleen nog leeftijd-verficatie. Dit moet via de app.",
                subtype=MessageType.plain,
            ),
        )

        await usersdata.update_one(
            {"_id": ObjectId(usr_id)}, {"$set": {"stripe_verified": True}}
        )

    if event_type == "identity.verification_session.canceled":
        print("User cancelled the identity request")

    return {"status": "success"}
