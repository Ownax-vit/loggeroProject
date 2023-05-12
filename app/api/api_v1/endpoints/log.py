from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_404_NOT_FOUND

from ....core.jwt import get_current_user_authorizer
from ....crud.log import get_list_logs
from ....db.mongodb import AsyncIOMotorClient
from ....db.mongodb import get_database
from ....models.log import ListLogRequest
from ....models.log import ListLogsInDb
from ....models.user import User

router = APIRouter(tags=["log"])


@router.get("/logs", status_code=HTTP_200_OK, response_model=ListLogsInDb)
async def get_logs(
    user: User = Depends(get_current_user_authorizer()),
    api_key_id: ListLogRequest = Body(...),
    db: AsyncIOMotorClient = Depends(get_database),
) -> ListLogsInDb:
    log_group = await get_list_logs(db, api_key_id.api_key_id, user.login)
    if not log_group:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Logs not found!")
    return ListLogsInDb(logs=log_group)
