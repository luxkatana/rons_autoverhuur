from datetime import datetime, timedelta, timezone
from typing import Annotated
from dotenv import load_dotenv
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from fastapi.responses import HTMLResponse
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from emailing import send_mail
from starlette.responses import JSONResponse

from routers.authentication_router import get_current_user_auth, get_current_user_data
from pydantic import BaseModel
from db import cars, authentication
from bson import ObjectId

from authentication import AuthUser, UserData
from os import environ
from db import payments_status, usersdata

from . import DatabaseCar
import stripe

load_dotenv()
stripe.api_key = environ["STRIPE_SECRET_KEY"]

StripeRouter = APIRouter(prefix="/stripe")
STRIPE_SUCCESS_URL = environ["STRIPE_SUCCESS_URL"]
STRIPE_CANCEL_URL = environ["STRIPE_CANCEL_URL"]


async def create_payment_document(authuser: AuthUser, car: DatabaseCar) -> ObjectId:
    payment = await payments_status.insert_one(
        {
            "user_id": ObjectId(authuser.id),
            "car_id": car.id,
            "status": "awaiting",
            # "payment_url": payment_url,
        }
    )
    return payment.inserted_id


class PaymentPayload(BaseModel):
    car_id: str  # The ID of the car
    # WARNING: THIS IS NOT DIRECTLY AN BSON OBJECTID


@StripeRouter.post("/rent-car")
async def rent_car(
    authuser: Annotated[AuthUser, Depends(get_current_user_auth)],
    userdata: Annotated[UserData, Depends(get_current_user_data)],
    payload: PaymentPayload,
):
    if userdata.email_verified is False:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Email is not yet verified")

    if userdata.stripe_verified is False:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Drivers license is not yet verified"
        )
    if userdata.verified is False:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Not yet verified, verify by opening a websocket connection at /ws-verify and sending then first the access token, and afterwards intercepting the message that the peer has sent",
        )

    try:
        result = await cars.find_one({"_id": ObjectId(payload.car_id)})
    except:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Object (car) id is invalid format"
        )
    if result is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Invalid car given or car is from VOS autoverhuur (Can't rent cars from VOS autoverhuur )",
        )
    car = DatabaseCar.model_validate(result)
    if car.available is False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Car is not available anymore")
    price = car.price
    price_in_cents: int = int(str(price).replace(".", ""))  # In cents actually
    product_name = f"De {car.brand} {car.model} {car.class_} {car.type}"
    tax = await stripe.TaxRate.create_async(
        display_name="BTW",
        inclusive=False,
        percentage=21,
        country="NL",
        description="Verplichte belasting voor niet-levensmiddelen",
    )
    payment_id: ObjectId = await create_payment_document(authuser, car)

    session = await stripe.checkout.Session.create_async(
        payment_method_types=["card", "ideal"],
        client_reference_id=str(payment_id),
        customer_email=authuser.email,
        line_items=[
            {
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": product_name,
                        #                        "images": [f"data:image/jpg;base64,{car.car_image_base64}"],
                    },
                    "unit_amount": price_in_cents,
                },
                "quantity": 1,
                "metadata": {"car_id": payload.car_id},
                "tax_rates": [tax.id],
            }
        ],
        mode="payment",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        success_url=f"{STRIPE_SUCCESS_URL}?session_id={str(payment_id)}",
        cancel_url=f"{STRIPE_CANCEL_URL}?session_id={str(payment_id)}",
    )
    await payments_status.update_one(
        {"_id": payment_id}, {"$set": {"payment_url": session.url}}
    )
    return {"payment_url": session.url}


async def send_email_success(userauth: dict[str, str], car: DatabaseCar):

    userdata = await usersdata.find_one({"_id": userauth["_id"]})
    product_name = f"{car.brand} {car.model} {car.class_} {car.type}"
    message = MessageSchema(
        subject=f"De betaling van de {product_name} is gelukt!",
        recipients=[
            userauth["email"]
        ],  # Gewoon gepakt bij chatGPT deze body, ik heb geen zin om een eigen html pagina te gaan schrijven
        body=f"""
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bevestiging Razende Ron's Autoverhuur</title>
    <style>
        body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #1a3c3c; color: #ffffff; }}
        .container {{ width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff; color: #333333; }}
        .header {{ background-color: #1a3c3c; padding: 40px; text-align: center; }}
        .header img {{ max-width: 250px; height: auto; }}
        .hero {{ background-color: #ff9900; color: #ffffff; padding: 20px; text-align: center; }}
        .content {{ padding: 30px; line-height: 1.6; }}
        .details-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        .details-table td {{ padding: 10px; border-bottom: 1px solid #eeeeee; }}
        .details-table td.label {{ font-weight: bold; color: #1a3c3c; }}
        .button-wrapper {{ text-align: center; padding: 30px; }}
        .button {{ background-color: #ff9900; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
        .footer {{ background-color: #f4f4f4; color: #777777; padding: 20px; text-align: center; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="https://raw.githubusercontent.com/luxkatana/rons_autoverhuur/main/assets/rra.png" alt="Razende Ron's Autoverhuur"/>
        </div>

        <div class="hero">
            <h1>Bedankt voor je boeking!</h1>
            <p>Je staat op het punt om plankgas te gaan.</p>
        </div>

        <div class="content">
            <p>Beste <strong>{userdata['firstname']}</strong>,</p>
            <p>Geweldig nieuws! Je betaling is succesvol ontvangen en je reservering bij <strong>Razende Ron's Autoverhuur</strong> is definitief bevestigd. Je gereserveerde <strong>{product_name}</strong> staat voor je klaar op de afgesproken datum.</p>
            
            <h3>Reserveringsdetails:</h3>
            <table class="details-table">
                <tr>
                    <td class="label">Reserveringsnummer:</td>
                    <td>#RR-123456</td>
                </tr>
                <tr>
                    <td class="label">Auto:</td>
                    <td>{product_name}</td>
                </tr>
                <tr>
                    <td class="label">Ophaaldatum:</td>
                    <td>[Datum] om [Tijd]</td>
                </tr>
                <tr>
                    <td class="label">Locatie:</td>
                    <td>Razende Rons Autoverhuur Vestiging Emmen, postcode 7825 </td>
                </tr>
            </table>

            <p>Heb je nog vragen? Stuur je vraag door naar de email <strong>R.matena@hondsrugcollege.nl</strong>
            <p>Met racy groet,<br>Team Razende Ron</p>
        </div>

        <div class="footer">
            <p>&copy; 2026 Razende Ron's Autoverhuur | Razende Rons Autoverhuur Vestiging, Emmen</p>
            <p>Je ontvangt deze mail omdat je een reservering hebt geplaatst.</p>
        </div>
    </div>
</body>
</html>


        """,
        subtype=MessageType.html,
    )
    await send_mail(message)


@StripeRouter.get("/identity-return")
async def identity_return():
    return HTMLResponse(
        "<!DOCTYPE html><html><body><h1>Mooizo, je krijgt zo een e-mail binnen 1 minuut die je vertelt als je identiteit is gelegitimeerd of niet.</h1></body></html>"
    )


@StripeRouter.get("/payment-success")
async def stripe_success(
    session_id: str, background_tasks: BackgroundTasks
) -> Response:
    payment_status_document = await payments_status.find_one(
        {"_id": ObjectId(session_id)}
    )
    if payment_status_document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    await cars.update_one(
        {"_id": payment_status_document["car_id"]}, {"$set": {"available": False}}
    )
    await payments_status.update_one(
        {"_id": payment_status_document["_id"]}, {"$set": {"status": "completed"}}
    )
    userauth: dict = await authentication.find_one(
        {"_id": payment_status_document["user_id"]}
    )
    background_tasks.add_task(
        send_email_success,
        userauth,
        DatabaseCar.model_validate(
            await cars.find_one({"_id": payment_status_document["car_id"]})
        ),
    )
    return Response(status_code=status.HTTP_200_OK)


@StripeRouter.get("/payment-cancel")
async def stripe_cancel(session_id: str) -> JSONResponse:
    payment_status_document = await payments_status.find_one(
        {"_id": ObjectId(session_id)}
    )
    if payment_status_document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await payments_status.update_one(
        {"_id": payment_status_document["_id"]}, {"$set": {"status": "cancelled"}}
    )
    return Response(status_code=status.HTTP_200_OK)
