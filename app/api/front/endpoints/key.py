from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi import Path
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_201_CREATED
from starlette.status import HTTP_204_NO_CONTENT
from starlette.status import HTTP_404_NOT_FOUND
from starlette.status import HTTP_502_BAD_GATEWAY

from ....core.jwt import get_current_user_authorizer
from ....crud.key import add_api_key
from ....crud.key import delete_api_key
from ....crud.key import get_api_key
from ....crud.key import get_api_keys
from ....crud.key import get_api_keys_by_journal
from ....crud.key import update_api_key
from ....db.mongodb import AsyncIOMotorClient
from ....db.mongodb import get_database
from ....models.key import KeyApiCreate
from ....models.key import KeyApiInResponse
from ....models.key import KeyApiUpdate
from ....models.key import ListKeysInResponse
from ....models.user import User

router = APIRouter(tags=["key"])


@router.get("/keys", status_code=HTTP_200_OK, response_model=ListKeysInResponse)
async def get_keys(
    user: User = Depends(get_current_user_authorizer()),
    db: AsyncIOMotorClient = Depends(get_database),
) -> ListKeysInResponse:
    key_api_group = await get_api_keys(db, user.login)
    if not key_api_group:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Api keys not found!"
        )
    return ListKeysInResponse(keys=key_api_group)


@router.get(
    "/keys/{journal_id}", status_code=HTTP_200_OK, response_model=ListKeysInResponse
)
async def get_keys_by_journal(
    journal_id: str = Path(...),
    user: User = Depends(get_current_user_authorizer()),
    db: AsyncIOMotorClient = Depends(get_database),
) -> ListKeysInResponse:
    key_api_group = await get_api_keys_by_journal(db, user.login, journal_id)
    if not key_api_group:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Api keys not found!"
        )
    return ListKeysInResponse(keys=key_api_group)


@router.post("/key", response_model=KeyApiInResponse, status_code=HTTP_201_CREATED)
async def create_key(
    key_api: KeyApiCreate = Body(...),
    user: User = Depends(get_current_user_authorizer()),
    db: AsyncIOMotorClient = Depends(get_database),
) -> KeyApiInResponse:
    dbkey = await add_api_key(db, key_api, user.login)
    if not dbkey:
        raise HTTPException(status_code=HTTP_502_BAD_GATEWAY, detail="Error create key")
    return KeyApiInResponse(**dbkey.dict())


@router.get("/key/{key_id}", response_model=KeyApiInResponse, status_code=HTTP_200_OK)
async def get_key(
    key_id: str = Path(...),
    user: User = Depends(get_current_user_authorizer()),
    db: AsyncIOMotorClient = Depends(get_database),
) -> KeyApiInResponse:
    dbkey = await get_api_key(db, key_id, user.login)
    if not dbkey:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Api key with current user not found!",
        )
    return KeyApiInResponse(**dbkey.dict())


@router.delete("/key/{key_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_key(
    key_id: str = Path(...),
    user: User = Depends(get_current_user_authorizer()),
    db: AsyncIOMotorClient = Depends(get_database),
):
    await delete_api_key(db, key_id, user.login)


@router.put("/key", status_code=HTTP_200_OK, response_model=KeyApiInResponse)
async def update_key(
    key: KeyApiUpdate = Body(...),
    user: User = Depends(get_current_user_authorizer()),
    db: AsyncIOMotorClient = Depends(get_database),
):
    dbkey = await update_api_key(db, key, user.login)
    if not dbkey:
        raise HTTPException(status_code=HTTP_502_BAD_GATEWAY, detail="Error update key")
    return KeyApiInResponse(**dbkey.dict())
