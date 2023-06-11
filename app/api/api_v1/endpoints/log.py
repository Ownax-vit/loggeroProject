from fastapi import APIRouter
from fastapi import Depends
from fastapi import Path
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_404_NOT_FOUND

from ....core.jwt import get_current_user_authorizer
from ....crud.log import get_list_logs_by_key_id
from ....db.mongodb import AsyncIOMotorClient
from ....db.mongodb import get_database
from ....models.log import ListLogsInDb
from ....models.user import User

router = APIRouter(tags=["log"])


@router.get("/logs/{key_id}", status_code=HTTP_200_OK, response_model=ListLogsInDb)
async def get_logs(
    key_id: str = Path(...),
    user: User = Depends(get_current_user_authorizer()),
    db: AsyncIOMotorClient = Depends(get_database),
) -> ListLogsInDb:
    log_group = await get_list_logs_by_key_id(db, key_id)
    if not log_group:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Logs not found!")
    return ListLogsInDb(logs=log_group)
