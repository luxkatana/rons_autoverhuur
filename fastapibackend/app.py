from typing import Annotated
from bson import ObjectId
from fastapi import Depends, FastAPI, Form, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer
import db
import authentication

api = FastAPI(docs_url="/")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="authenticate")


async def get_current_user_auth(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> authentication.AuthUser:
    user_id = authentication.decode_jwt(token)
    authuser = await db.authentication.find_one({"_id": ObjectId(user_id)})
    return authentication.AuthUser.from_database(authuser)


async def get_current_user_data(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> authentication.UserData:
    user_id = authentication.decode_jwt(token)
    userdata = await db.usersdata.find_one({"_id": ObjectId(user_id)})
    if userdata is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No user found with given _id")
    return authentication.UserData.from_database(userdata)


@api.get("/hi", status_code=status.HTTP_200_OK)
async def hi():  # Just send 200
    return Response()


@api.post("/authenticate", summary="Endpoint to authenticate/login")
async def login(
    email: str = Form(description="The e-mail", default="testuser67@gmail.com"),
    password: str = Form(
        description="The password raw (not hashed)", default="wachtwoord"
    ),
) -> dict[str, str]:
    auth_user = await authentication.get_auth_user(email, password)
    if auth_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    jwt_token = authentication.generate_jwt_token(auth_user)
    return {"access_token": jwt_token, "token_type": "bearer"}


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
