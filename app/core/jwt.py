from datetime import datetime
from datetime import timedelta
from typing import Optional

import jwt
from fastapi import Cookie
from fastapi import Depends
from fastapi import Header
from jwt.exceptions import PyJWTError
from starlette.exceptions import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.status import HTTP_404_NOT_FOUND

from ..crud.user import get_user
from ..db.mongodb import AsyncIOMotorClient
from ..db.mongodb import get_database
from ..models.token import TokenPayload
from ..models.user import User
from .config import ACCESS_TOKEN_EXPIRE_MINUTES
from .config import JWT_TOKEN_PREFIX
from .config import REFRESH_TOKEN_EXPIRE_MINUTES
from .config import SECRET_KEY


ALGORITHM = "HS256"
access_token_jwt_subject = "access"
refresh_token_jwt_subject = "refresh"


def _get_authorization_token(authorization: str = Header(...)):
    token_prefix, token = authorization.split(" ")
    if token_prefix != JWT_TOKEN_PREFIX:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization type token ",
        )
    return token


def _get_authorization_token_refresh(refresh_token: str = Cookie(...)):
    token = _get_authorization_token(refresh_token)
    return token


async def _get_current_user(
    db: AsyncIOMotorClient = Depends(get_database),
    token: str = Depends(_get_authorization_token),
) -> User:
    try:
        payload = jwt.decode(token, str(SECRET_KEY), algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except PyJWTError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
        )
    dbuser = await get_user(db, token_data.login)
    if not dbuser:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")

    user = User(**dbuser.dict(), token=token)
    return user


async def get_current_user_refresh(
    db: AsyncIOMotorClient = Depends(get_database),
    token: str = Depends(_get_authorization_token_refresh),
) -> User:
    user = await _get_current_user(db, token)
    return user


def _get_authorization_token_optional(authorization: str = Header(None)):
    if authorization:
        return _get_authorization_token(authorization)
    return ""


async def _get_current_user_optional(
    db: AsyncIOMotorClient = Depends(get_database),
    token: str = Depends(_get_authorization_token_optional),
) -> Optional[User]:
    if token:
        return await _get_current_user(db, token)

    return None


def get_current_user_authorizer(*, required: bool = True):
    if required:
        return _get_current_user
    else:
        return _get_current_user_optional


def create_token(data: dict, expire: datetime, token_sub: str):
    to_encode = data.copy()
    to_encode.update({"exp": expire, "sub": token_sub})
    encoded_jwt = jwt.encode(to_encode, str(SECRET_KEY), algorithm=ALGORITHM)
    return encoded_jwt


def create_access_token(*, data: dict, expires_delta: Optional[timedelta] = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_token(data, expire, access_token_jwt_subject)
    return token


def create_refresh_token(*, data: dict, expires_delta: Optional[timedelta] = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    token = create_token(data, expire, refresh_token_jwt_subject)
    return token
