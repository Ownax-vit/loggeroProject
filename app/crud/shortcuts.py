from datetime import datetime
from typing import Optional

from pydantic import EmailStr
from starlette.exceptions import HTTPException
from starlette.status import (
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_404_NOT_FOUND,
    HTTP_410_GONE
)

from ..db.mongodb import AsyncIOMotorClient
from .user import get_user
from .user import get_user_by_email
from .key import get_api_key_by_token

async def check_free_username_and_email(
    conn: AsyncIOMotorClient,
    login: Optional[str] = None,
    email: Optional[EmailStr] = None,
):
    if login:
        user_by_username = await get_user(conn, login)
        if user_by_username:
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail="User with this username already exists",
            )
    if email:
        user_by_email = await get_user_by_email(conn, email)
        if user_by_email:
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail="User with this email already exists",
            )


async def check_token(conn: AsyncIOMotorClient,
                      token: str) -> Optional[str]:
    """ Check token api-key by date """
    token = await get_api_key_by_token(conn, token)
    if token is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Current api-key not found!"
        )
    if token.expire < datetime.now():
        raise HTTPException(
            status_code=HTTP_410_GONE,
            detail="Current token expired!"
        )
    return token.id

