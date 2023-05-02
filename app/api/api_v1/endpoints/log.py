from fastapi import APIRouter, Body
from fastapi import Depends
from fastapi import Path
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_200_OK,  HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND

from ....core.jwt import get_current_user_authorizer
from ....models.log import LogInDb, LogRequest, ListLogsShow, ListLogRequest
from ....db.mongodb import get_database
from ....db.mongodb import AsyncIOMotorClient
from ....crud.log import add_log, get_list_logs
from ....models.user import User

router = APIRouter(tags=["log"])


@router.get("/logs", status_code=HTTP_200_OK, response_model=ListLogsShow)
async def get_logs(
    user: User = Depends(get_current_user_authorizer()),
    api_key_id: ListLogRequest = Body(...),
    db: AsyncIOMotorClient = Depends(get_database),
) -> ListLogsShow:
    log_group = await get_list_logs(db, api_key_id.api_key_id, user.login)
    if not log_group:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Logs not found!"
        )
    return ListLogsShow(logs=log_group)

