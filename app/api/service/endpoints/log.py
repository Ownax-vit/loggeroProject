from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi import Path
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_200_OK,  HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND

from ....models.log import LogInDb, LogRequest
from ....db.mongodb import get_database
from ....db.mongodb import AsyncIOMotorClient
from ....crud.log import add_log

router = APIRouter(tags=["log"])


@router.post("/log", response_model=LogInDb, status_code=HTTP_201_CREATED)
async def push_log(
    log: LogRequest = Body(...),
    db: AsyncIOMotorClient = Depends(get_database),
) -> LogInDb:
    dbLog = await add_log(db, log)
    return LogInDb(**dbLog.dict())

