from typing import Optional

from starlette.exceptions import HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from ..core.config import database_name
from ..core.config import log_collection_name
from ..db.mongodb import AsyncIOMotorClient
from ..models.log import LogRequest, LogInDb, ListLogsShow
from .shortcuts import check_token
from .key import get_api_key


async def add_log(
    conn: AsyncIOMotorClient, log: LogRequest) -> LogInDb:
    """ Push log in DB from host by api-key token"""

    token_from = log.api_key_public
    key_id = await check_token(conn, token_from)
    dbLog = LogInDb(**log.dict(), api_key_id=key_id)
    await conn[database_name][log_collection_name].insert_one(dbLog.dict(by_alias=True))

    return dbLog


async def get_list_logs(conn: AsyncIOMotorClient, api_key_id, login) -> Optional[ListLogsShow]:
    dbkey = await get_api_key(conn, api_key_id, login)
    if not dbkey:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                            detail="Api key not found!")

    logs = [
        LogInDb(**log)
        async for log in conn[database_name][log_collection_name].find({"api_key_id": api_key_id})
    ]
    if logs:
        return logs
