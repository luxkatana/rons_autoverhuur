from typing import Annotated
from fastapi import Depends, FastAPI, Response, status
from routers import (
    AuthenticationRouter,
    VerificationRouter,
    CarsRouter,
    StripeWebhooksRouter,
    StripeRouter,
    get_current_user_auth,
    get_current_user_data,
)
import authentication

api = FastAPI(docs_url="/")
api.include_router(AuthenticationRouter, prefix="/auth")
api.include_router(StripeWebhooksRouter)
api.include_router(VerificationRouter)
api.include_router(CarsRouter)
api.include_router(StripeRouter)


@api.get("/hi", status_code=status.HTTP_200_OK)
async def hi():  # Just send 200
    return Response()


@api.get("/me")
async def me(
    authuser: Annotated[authentication.AuthUser, Depends(get_current_user_auth)],
):
    return {"_id": authuser.id, "email": authuser.email}


@api.get("/userdata")
async def get_userdata(
    userdata: Annotated[authentication.UserData, Depends(get_current_user_data)],
) -> authentication.UserData:
    return userdata
