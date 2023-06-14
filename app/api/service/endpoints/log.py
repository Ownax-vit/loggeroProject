from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi import WebSocket
from starlette.status import HTTP_201_CREATED

from ....core.ws import WSAccessor
from ....core.ws import WSContext
from ....core.ws import WSLogger
from ....core.ws import WSManager
from ....crud.log import add_log
from ....db.mongodb import AsyncIOMotorClient
from ....db.mongodb import get_database
from ....models.log import LogInDb
from ....models.log import LogRequest


router = APIRouter(tags=["log"])

ws_accessor = WSAccessor()
ws_logger = WSLogger()
ws_manager = WSManager(ws_accessor, ws_logger)


@router.post("/log", response_model=LogInDb, status_code=HTTP_201_CREATED)
async def push_log(
    log: LogRequest = Body(...),
    db: AsyncIOMotorClient = Depends(get_database),
) -> LogInDb:
    db_log = await add_log(db, log)
    return LogInDb(**db_log.dict())


@router.websocket("/ws/{token}")
async def websocket_connect(
    websocket: WebSocket, token: str, db: AsyncIOMotorClient = Depends(get_database)
):
    """Connection on socket by api-key of machine"""
    async with WSContext(ws_manager, websocket, token) as connection_object:
        await ws_manager.handle(connection_object, token, db)
