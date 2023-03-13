
from fastapi import APIRouter, Body, Depends
from fastapi import status
from fastapi.exceptions import HTTPException
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from ....core.jwt import get_current_user_authorizer

from ....crud.key import add_api_key, get_api_keys, delete_api_key
from ....db.mongodb import AsyncIOMotorClient, get_database
from ....models.key import KeyApiDelete, KeyApiCreate, KeyApiInResponse, ListKeysInResponse
from ....models.user import User

router = APIRouter(tags=["key"])


@router.get("/api-keys", response_model=ListKeysInResponse)
async def get_keys(
        # user: User = Depends(get_current_user_authorizer()),
        db: AsyncIOMotorClient = Depends(get_database),
) -> ListKeysInResponse:
    key_api_group = await get_api_keys(db, "ownax")
    if not key_api_group:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Api keys not found!"
        )
    return ListKeysInResponse(keys=key_api_group)


@router.post("/api-keys", response_model=KeyApiInResponse)
async def create_key(
        key_api: KeyApiCreate = Body(..., embed=True),
        # user: User = Depends(get_current_user_authorizer()),
        db: AsyncIOMotorClient = Depends(get_database),
) -> KeyApiInResponse:
    dbkey = await add_api_key(db, key_api, "ownax")
    return KeyApiInResponse(**dbkey.dict())


@router.delete("/api-keys", status_code=HTTP_204_NO_CONTENT)
async def delete_key(
        key_api: KeyApiDelete = Body(..., embed=True),
        # user: User = Depends(get_current_user_authorizer()),
        db: AsyncIOMotorClient = Depends(get_database),
):
    await delete_api_key(db, key_api.token)




