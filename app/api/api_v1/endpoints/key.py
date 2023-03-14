from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_201_CREATED
from starlette.status import HTTP_204_NO_CONTENT
from starlette.status import HTTP_403_FORBIDDEN
from starlette.status import HTTP_404_NOT_FOUND

from ....core.jwt import get_current_user_authorizer
from ....crud.key import add_api_key
from ....crud.key import delete_api_key
from ....crud.key import get_api_keys
from ....crud.key import update_api_key
from ....db.mongodb import AsyncIOMotorClient
from ....db.mongodb import get_database
from ....models.key import KeyApiCreate
from ....models.key import KeyApiDelete
from ....models.key import KeyApiInResponse
from ....models.key import KeyApiUpdate
from ....models.key import ListKeysInResponse
from ....models.user import User

router = APIRouter(tags=["key"])


@router.get("/api-keys", status_code=HTTP_200_OK, response_model=ListKeysInResponse)
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


@router.post("/api-keys", response_model=KeyApiInResponse, status_code=HTTP_201_CREATED)
async def create_key(
    key_api: KeyApiCreate = Body(..., embed=True),
    user: User = Depends(get_current_user_authorizer()),
    db: AsyncIOMotorClient = Depends(get_database),
) -> KeyApiInResponse:
    dbkey = await add_api_key(db, key_api, user.login)
    return KeyApiInResponse(**dbkey.dict())


@router.delete("/api-keys", status_code=HTTP_204_NO_CONTENT)
async def delete_key(
    key_api: KeyApiDelete = Body(..., embed=True),
    user: User = Depends(get_current_user_authorizer()),
    db: AsyncIOMotorClient = Depends(get_database),
):
    if not user:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Not allowed for user!"
        )
    await delete_api_key(db, key_api.token)


@router.put("/api-keys", status_code=HTTP_200_OK, response_model=KeyApiInResponse)
async def update_key(
    key_api: KeyApiUpdate = Body(..., embed=True),
    user: User = Depends(get_current_user_authorizer()),
    db: AsyncIOMotorClient = Depends(get_database),
):
    dbkey = await update_api_key(db, user.login, key_api)

    return KeyApiInResponse(**dbkey.dict())
