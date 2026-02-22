from typing import Annotated
from fastapi import Depends, FastAPI, Response, status
from routers.authentication_router import (
    AuthenticationRouter,
    get_current_user_auth,
    get_current_user_data,
)
import authentication

api = FastAPI(docs_url="/")
api.include_router(AuthenticationRouter, prefix="/auth")


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
