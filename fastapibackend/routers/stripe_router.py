from datetime import datetime, timedelta, timezone
from typing import Annotated
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Response, status
from starlette.responses import JSONResponse

from routers.authentication_router import get_current_user_auth
from pydantic import BaseModel
from db import cars
from bson import ObjectId

from authentication import AuthUser
from os import environ
from db import payments_status

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
    payload: PaymentPayload,
):
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


@StripeRouter.get("/payment-success")
async def stripe_success(session_id: str) -> Response:
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
