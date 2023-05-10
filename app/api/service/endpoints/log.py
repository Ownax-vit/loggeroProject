from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi import WebSocket
from starlette.status import HTTP_201_CREATED

from ....core.ws import WSAccessor
from ....core.ws import WSContext
from ....core.ws import WSManager
from ....crud.log import add_log
from ....db.mongodb import AsyncIOMotorClient
from ....db.mongodb import get_database
from ....models.log import LogInDb
from ....models.log import LogRequest


router = APIRouter(tags=["log"])

ws_accessor = WSAccessor()
ws_manager = WSManager(ws_accessor)


@router.post("/log", response_model=LogInDb, status_code=HTTP_201_CREATED)
async def push_log(
    log: LogRequest = Body(...),
    db: AsyncIOMotorClient = Depends(get_database),
) -> LogInDb:
    dbLog = await add_log(db, log)
    return LogInDb(**dbLog.dict())


@router.websocket("/ws/{token}")
async def websocket_connect(
    websocket: WebSocket, token: str, db: AsyncIOMotorClient = Depends(get_database)
):
    """принимает соединение по сокету, использует токен клиента"""
    async with WSContext(ws_manager, websocket) as connection_object:
        await ws_manager.handle(connection_object, token, db)
