from concurrent.futures import ProcessPoolExecutor
from typing import Annotated
from bson import ObjectId
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from dateutil.relativedelta import relativedelta
from fastapi.responses import HTMLResponse
from authentication import AuthUser
from .authentication_router import WS_get_current_user_data
from db import usersdata
import asyncio
from datetime import datetime
from fastmrz import FastMRZ

VerificationRouter = APIRouter()
executor = ProcessPoolExecutor()


def verify_idcard(base64_img: str) -> dict[str, str]:
    mrz_detection = FastMRZ()
    id_card_parsed_info = mrz_detection.get_details(base64_img, "base64")
    return id_card_parsed_info


async def age_check_loop(websocket: WebSocket) -> bool | dict[str, str]:
    await websocket.send_text("Yo gimme that juicy base64 image")
    received_base64 = await websocket.receive_text()
    loop = asyncio.get_running_loop()
    id_card_parsed_info = await loop.run_in_executor(
        executor, verify_idcard, received_base64
    )
    birthdate = datetime.strptime(id_card_parsed_info["birth_date"], "%Y-%m-%d")
    years_diff = (relativedelta(datetime.now(), birthdate)).years
    if years_diff < 18:
        await websocket.send_json(
            {
                "success": False,
                "errorno": 1,
                "description": f"User is {years_diff}, but has to be 18 or older",
            }
        )
        return False
    await websocket.send_json(
        {
            "age": years_diff,
            "youdothis": "Reply with 'y' if correct or send manual date e.g 2025-05-28",
        }
    )
    while True:
        reply: str = await websocket.receive_text()
        if reply != "y":
            try:
                birthdate = datetime.strptime(reply, "%Y-%m-%d")
            except ValueError:  # Likely wrong format
                await websocket.send_json(
                    {
                        "success": False,
                        "errorno": 2,
                        "description": "Date is not correct format",
                    }
                )
                continue
            years_diff = (relativedelta(datetime.now(), birthdate)).years
            if years_diff < 18:
                await websocket.send_json(
                    {
                        "success": False,
                        "errorno": 1,
                        "description": f"User is {years_diff} years old (minor)",
                    }
                )
                return False
        break

    await websocket.send_json({"age": years_diff, "success": True})
    return {
        "birthdate": birthdate,
        "age": years_diff,
        "mrz_id_card": id_card_parsed_info,
    }


@VerificationRouter.get("/email-verify")
async def email_verify(user_id: str):
    try:
        buser_id = ObjectId(user_id)
    except TypeError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    await usersdata.update_one({"_id": buser_id}, {"$set": {"email_verified": True}})
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <body>
    <h1> Geverifieerd! Je mag nu deze pagina sluiten </h1>
    </body>
    </html>

""")


@VerificationRouter.websocket("/ws-verify", name="Verify legal documents")
async def ws_verify(
    websocket: WebSocket,
    userdata: Annotated[AuthUser, Depends(WS_get_current_user_data)],
):
    if userdata is None:
        return
    # await websocket.accept()
    try:
        status: bool | dict[str, str] = await age_check_loop(websocket)
        if isinstance(status, bool) is True:
            return
        info: dict[str, str] = status
        # Find the user, and change the flag to true, and yeah also fill in the additional info
        await usersdata.find_one_and_update(
            {"_id": ObjectId(userdata.id)},
            {
                "$set": {
                    "verified": True,
                    "firstname": info["mrz_id_card"]["given_name"].capitalize(),
                    "lastname": info["mrz_id_card"]["surname"].capitalize(),
                    "birthdate": info["birthdate"],
                }
            },
        )

    except WebSocketDisconnect:
        ...
    else:
        await websocket.close()
