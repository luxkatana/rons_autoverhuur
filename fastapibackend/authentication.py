from datetime import date, datetime, timedelta, timezone
from pydantic import BaseModel, Field, PrivateAttr
from typing import Annotated
from fastapi import Depends
import pymongo
from db import authentication, usersdata
import jwt
import pwdlib

SALT: str = (
    "BariumSulfaat"  # This must be random, but for now, idc -- this is btw for the pwdlib
)
SECRET_KEY = "a5c4903f310215cab8d7c4e1719852778052cd25eb5b4ecff6512e5095fcf25c"  #  This is for the JWT token generation
ALGORITHM = "HS256"
password_hasher = pwdlib.PasswordHash.recommended()


def hash_password(rawpassword: str) -> str:
    return password_hasher.hash(rawpassword, salt=SALT)


class Token(BaseModel):
    access_token: str
    token_type: str


class UserData(BaseModel):  # From the userdata collectin
    id: str
    firstname: str
    lastname: str
    verified: bool
    birthdate: date


class AuthUser(BaseModel):
    id: str
    email: str
    password: str


async def get_auth_user(email: str, password_hash: str) -> AuthUser | None:
    auth_user = await authentication.find_one(
        {"email": email, "password": password_hash}
    )
    if auth_user is None:
        return None
    return AuthUser(
        id=str(auth_user["_id"]),
        email=auth_user["email"],
        password=auth_user["password"],
    )


async def get_userdata(
    authuser: Annotated[AuthUser, Depends(get_auth_user)],
) -> AuthUser | None:
    returned_userdata = await usersdata.find({"_id": authuser.id})
    if returned_userdata is None:
        return None
    # WARNING: Convert _id to id
    return UserData(**returned_userdata)


def generate_jwt_token(authuser: AuthUser) -> Token:
    # NOTE: It's probably a good idea to have a delta time (expire time)
    # Nvm let's keep it simple, 5 minutes for now?
    payload = {
        "id": authuser.id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
