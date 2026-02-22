from httpx import ASGITransport, AsyncClient, Response
import asyncio
import pytest
from app import api


@pytest.mark.asyncio(loop_scope="class")
class TestApi:
    loop: asyncio.AbstractEventLoop

    async def get_authenticated_client(self) -> AsyncClient:
        client = AsyncClient(transport=ASGITransport(api), base_url="http://test")
        response = await client.post(
            "/authenticate",
            data={"email": "testuser67@gmail.com", "password": "wachtwoord"},
        )

        access_token = response.raise_for_status().json().get("access_token", False)
        assert isinstance(access_token, str) is True
        client.headers["Authorization"] = f"Bearer {access_token}"
        return client

    async def test_me(self):
        client = await self.get_authenticated_client()
        response = await client.get("/me")
        response.raise_for_status()

    async def test_userdata(self):
        client = await self.get_authenticated_client()
        response = await client.get("/userdata")
        response.raise_for_status()
        print(response.json())
