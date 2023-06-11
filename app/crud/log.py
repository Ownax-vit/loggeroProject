from typing import List
from typing import Optional

from fastapi import WebSocketException
from starlette.exceptions import HTTPException
from starlette.status import HTTP_404_NOT_FOUND
from starlette.status import HTTP_502_BAD_GATEWAY

from ..core.config import database_name
from ..core.config import log_collection_name
from ..db.mongodb import AsyncIOMotorClient
from ..models.base import PyObjectId
from ..models.log import LogInDb
from ..models.log import LogRequest
from .shortcuts import check_token


async def add_log(conn: AsyncIOMotorClient, log: LogRequest) -> LogInDb:
    """Push log in DB"""
    token_from = log.api_key_public
    key_id = await check_token(conn, token_from)
    dbLog = LogInDb(**log.dict(), api_key_id=key_id)
    res = await conn[database_name][log_collection_name].insert_one(
        dbLog.dict(by_alias=True)
    )
    if not res:
        raise HTTPException(
            status_code=HTTP_502_BAD_GATEWAY, detail="Error insert log to database"
        )
    return dbLog


async def add_log_ws(conn: AsyncIOMotorClient, log: LogRequest) -> LogInDb:
    """Push log in DB from app (websocket) by api-key token"""
    try:
        log = await add_log(conn, log)
        return log
    except HTTPException as exc:
        raise WebSocketException(code=1014, reason=exc.detail)


async def get_list_logs_by_key_id(
    conn: AsyncIOMotorClient, key_id: str
) -> Optional[List[LogInDb]]:
    logs = [
        LogInDb(**log)
        async for log in conn[database_name][log_collection_name].find(
            {"api_key_id": PyObjectId(key_id)}
        )
    ]
    if logs:
        return logs


async def remove_logs_by_key_id(conn: AsyncIOMotorClient, key_id: str | PyObjectId):
    res = await conn[database_name][log_collection_name].delete_many(
        {"api_key_id": PyObjectId(key_id)}
    )
    if not res:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Error remove logs by key"
        )
