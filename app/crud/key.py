import uuid
from datetime import datetime
from datetime import timedelta
from typing import List
from typing import Optional

from starlette.exceptions import HTTPException
from starlette.status import HTTP_404_NOT_FOUND
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from ..core.config import API_KEY_EXPIRE_DAYS
from ..core.config import database_name
from ..core.config import key_collection_name
from ..db.mongodb import AsyncIOMotorClient
from ..models.key import KeyApiCreate
from ..models.key import KeyApiInDB
from ..models.key import KeyApiInResponse
from ..models.key import KeyApiUpdate


async def add_api_key(
    conn: AsyncIOMotorClient, key: KeyApiCreate, login: str
) -> KeyApiInDB:
    token = str(uuid.uuid4())
    expire = datetime.utcnow() + timedelta(API_KEY_EXPIRE_DAYS)
    dbkey = KeyApiInDB(**key.dict(), login=login, token=token, expire=expire)

    await conn[database_name][key_collection_name].insert_one(dbkey.dict())

    return dbkey


async def get_api_keys(
    conn: AsyncIOMotorClient, login: str
) -> Optional[List[KeyApiInResponse]]:
    keys = [
        KeyApiInResponse(**key)
        async for key in conn[database_name][key_collection_name].find({"login": login})
    ]
    if keys:
        return keys


async def get_api_key(conn: AsyncIOMotorClient, key: str) -> KeyApiInDB:
    dbkey = await conn[database_name][key_collection_name].find_one({"token": key})
    if dbkey:
        return KeyApiInDB(**dbkey)


async def delete_api_key(conn: AsyncIOMotorClient, key: str):
    await conn[database_name][key_collection_name].delete_one({"token": key})


async def update_api_key(
    conn: AsyncIOMotorClient, login: str, key: KeyApiUpdate
) -> KeyApiInDB | None:
    dbkey = await get_api_key(conn, key.token)
    if not dbkey:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Api key not found!")

    new_token = str(uuid.uuid4())
    expire = datetime.utcnow() + timedelta(API_KEY_EXPIRE_DAYS)

    dbkey.token = new_token
    dbkey.expire = expire
    dbkey.login = login
    dbkey.name = key.name or dbkey.name
    dbkey.description = key.description or dbkey.description

    res = await conn[database_name][key_collection_name].update_one(
        {"token": key.token}, {"$set": dbkey.dict()}
    )
    if res.modified_count != 1:
        raise HTTPException(
            HTTP_422_UNPROCESSABLE_ENTITY, detail="Error while update api key"
        )

    return dbkey
