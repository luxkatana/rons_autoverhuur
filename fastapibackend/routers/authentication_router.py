"""
Authentication router
- /authenticate  -> login and retrieve access token
- /sign-up ->

"""

from datetime import datetime, timezone
from fastapi import APIRouter, Form, status, HTTPException, Depends, Response
from bson import ObjectId
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field
import authentication, db

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


AuthenticationRouter = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


@AuthenticationRouter.post("/authenticate", summary="Endpoint to authenticate/login")
async def login(
    email: EmailStr = Form(description="The e-mail", default="testuser67@gmail.com"),
    password: str = Form(
        description="The password raw (not hashed)", default="wachtwoord"
    ),
) -> Token:
    auth_user = await authentication.get_auth_user(email, password)
    if auth_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    jwt_token = authentication.generate_jwt_token(auth_user)
    return Token(access_token=jwt_token)


@AuthenticationRouter.delete(
    "/sign-up", summary="Remove test account", status_code=status.HTTP_200_OK
)
async def delete_test_account() -> Response:
    deleted_document = await db.authentication.find_one_and_delete(
        {"email": "testcreate@gmail.com"}
    )
    if deleted_document is not None:
        await db.usersdata.delete_one({"_id": deleted_document["_id"]})
    return Response()


@AuthenticationRouter.post(
    "/sign-up",
    summary="Create an account",
    responses={
        201: {
            "description": "Account created successfully",
            "content": {
                "application/json": {
                    "example": {"access_token": "string", "token_type": "bearer"}
                }
            },
        },
        422: {"description": "Validation error or e-mail exists"},
    },
)
async def signup(signupform: SignupInputForm) -> Response:  # e-mail is unique
    existing_user = await db.authentication.find_one({"email": signupform.email})
    if existing_user is not None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, detail="e-mail already exists"
        )
    newauthentication = await db.authentication.insert_one(
        {
            "password": authentication.hash_password(signupform.password),
            "email": signupform.email,
        }
    )
    await db.usersdata.insert_one(
        {
            "_id": newauthentication.inserted_id,
            "firstname": signupform.firstname,
            "lastname": signupform.lastname,
            "birthdate": datetime(1, 1, 1, tzinfo=timezone.utc),
            "verified": False,
        }
    )
    newtoken = await login(signupform.email, signupform.password)
    return Response(
        status_code=status.HTTP_201_CREATED,
        content=newtoken.model_dump_json(),
        media_type="application/json",
    )


class SignupInputForm(BaseModel):
    firstname: str = Field(description="Your first name", default="Justin")
    lastname: str = Field(
        description="Your last name (include your prefixes here if any)",
        default="Case",
    )
    email: EmailStr = Field(default="testcreate@gmail.com")
    password: str = Field(
        description="Your password (must have atleast 8 characters)",
        min_length=8,
        max_length=20,
        default="letmeinpls",
    )
