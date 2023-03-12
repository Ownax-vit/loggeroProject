
from fastapi import APIRouter, Body, Depends
from fastapi import status
from fastapi.exceptions import HTTPException

from ....core.jwt import get_current_user_authorizer

from ....crud.key import add_key
from ....db.mongodb import AsyncIOMotorClient, get_database
from ....models.key import KeyApiCreate, KeyApiInResponse, KeyApiInDB
from ....models.user import User

router = APIRouter(tags=["key"])


@router.post("/create_key", response_model=KeyApiInResponse)
async def create_key(
        key_api: KeyApiCreate = Body(..., embed=True),
        user: User = Depends(get_current_user_authorizer()),
        db: AsyncIOMotorClient = Depends(get_database),
) -> KeyApiInResponse:
    dbkey = await add_key(db, key_api, user.login)
    return KeyApiInResponse(key=KeyApiInDB(**dbkey.dict()))
