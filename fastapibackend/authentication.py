from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from typing import Annotated
from fastapi import Depends
from db import authentication, usersdata
import jwt
import pwdlib

SALT: str = (
    "ammoniumsulfide"  # This must be random, but for now, idc -- this is btw for the pwdlib
).encode()
SECRET_KEY = "a5c4903f310215cab8d7c4e1719852778052cd25eb5b4ecff6512e5095fcf25c"  #  This is for the JWT token generation
ALGORITHM = "HS256"
password_hasher = pwdlib.PasswordHash.recommended()


def hash_password(rawpassword: str) -> str:
    return password_hasher.hash(rawpassword, salt=SALT)


def verify_hashes(original_hash: str, rawpassword: str) -> bool:
    return original_hash == hash_password(rawpassword)


def decode_jwt(jwttoken: str) -> str:
    """
    Returns the ID of the user (the _id field in mongodb)
    """
    return jwt.decode(jwttoken, SECRET_KEY, ALGORITHM)["id"]


class UserData(BaseModel):  # From the userdata collectin
    id: str
    firstname: str
    lastname: str
    verified: bool
    stripe_verified: bool
    birthdate: datetime

    @classmethod
    def from_database(cls, databasereply: dict[str, str]) -> UserData:
        databasereply["id"] = str(databasereply.pop("_id"))
        return cls(**databasereply)


class AuthUser(BaseModel):
    id: str
    email: str
    password: str

    @classmethod
    def from_database(cls, databasereply: dict[str, str]) -> AuthUser:
        databasereply["id"] = str(
            databasereply.pop("_id")
        )  # Conversion, _id is in pydantic private and for god's sake i cant access that
        return cls(**databasereply)


async def get_auth_user(email: str, password: str) -> AuthUser | None:
    password_hash = hash_password(password)
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


def generate_jwt_token(authuser: AuthUser) -> str:
    # NOTE: It's probably a good idea to have a delta time (expire time)
    # Nvm let's keep it simple, 5 minutes for now?
    payload = {
        "id": authuser.id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
