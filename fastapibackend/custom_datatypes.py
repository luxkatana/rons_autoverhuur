from typing import Annotated
from fastapi import Form


class CustomOAuth2PasswordRequestForm:

    def __init__(
        self,
        *,
        email: Annotated[
            str,
            Form(),
            # WARNING: Customised here
            """
                WARNING: This has been customised, usually you need to send the username, but in this project the username is just not unique enough to my opinion
                """,
        ],
        password: Annotated[
            str,
            Form(json_schema_extra={"format": "password"}),
        ],
        client_id: Annotated[
            str | None,
            Form(),
        ] = None,
        client_secret: Annotated[
            str | None,
            Form(json_schema_extra={"format": "password"}),
        ] = None,
    ):
        self.email = email
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
