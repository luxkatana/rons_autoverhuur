from fastapi import Depends, FastAPI, HTTPException, status
import authentication
from custom_datatypes import *

api = FastAPI()


@api.post("/authenticate")
async def login(
    form_data: Annotated[CustomOAuth2PasswordRequestForm, Depends()],
) -> (
    authentication.Token
):  # Takes in email, password (HASH), client_secret, client_id and grant_type
    password_hash = form_data.password
    email = form_data.email
    auth_user = await authentication.get_auth_user(email, password_hash)
    if auth_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    jwt_token = authentication.generate_jwt_token(auth_user)
    return authentication.Token(access_token=jwt_token, token_type="bearer")
