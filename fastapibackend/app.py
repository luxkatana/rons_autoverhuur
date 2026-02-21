from typing import Annotated
from bson import ObjectId
from fastapi import Depends, FastAPI, Form, HTTPException, status
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


@api.post("/authenticate", summary="Endpoint to authenticate/login")
async def login(
    email: str = Form(description="The e-mail", default="testuser67@gmail.com"),
    password: str = Form(
        description="The password raw (not hashed)", default="wachtwoord"
    ),
) -> (
    authentication.Token
):  # Takes in email, password (HASH), client_secret, client_id and grant_type
    auth_user = await authentication.get_auth_user(email, password)
    if auth_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    jwt_token = authentication.generate_jwt_token(auth_user)
    return authentication.Token(access_token=jwt_token, token_type="bearer")


@api.get("/me")
async def me(
    token: Annotated[authentication.AuthUser, Depends(get_current_user_auth)],
):
    return {"_id": token.id, "email": token.email}
