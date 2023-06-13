import uuid
from datetime import datetime
from datetime import timedelta
from typing import List
from typing import Optional

import bson
from starlette.exceptions import HTTPException
from starlette.status import HTTP_404_NOT_FOUND
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from starlette.status import HTTP_502_BAD_GATEWAY

from ..core.config import API_KEY_EXPIRE_DAYS
from ..core.config import database_name
from ..core.config import key_collection_name
from ..crud.journal import push_journal_token
from ..crud.journal import remove_journal_token_from_preview
from ..db.mongodb import AsyncIOMotorClient
from ..models.base import PyObjectId
from ..models.key import KeyApiCreate
from ..models.key import KeyApiInDB
from ..models.key import KeyApiPreview
from ..models.key import KeyApiUpdate


async def add_api_key(
    conn: AsyncIOMotorClient, key: KeyApiCreate, login: str
) -> KeyApiInDB:
    """Create api key and link to journal"""
    token = str(uuid.uuid4())
    expire = datetime.utcnow() + timedelta(API_KEY_EXPIRE_DAYS)
    dbkey = KeyApiInDB(**key.dict(), login=login, token=token, expire=expire)

    res = await conn[database_name][key_collection_name].insert_one(
        dbkey.dict(by_alias=True)
    )
    if not res:
        raise HTTPException(
            status_code=HTTP_502_BAD_GATEWAY, detail="Error insert key to database"
        )

    await push_journal_token(conn, dbkey.journal_id, KeyApiPreview(**dbkey.dict()))

    return dbkey


async def get_api_keys(
    conn: AsyncIOMotorClient, login: str
) -> Optional[List[KeyApiInDB]]:
    keys = [
        KeyApiInDB(**key)
        async for key in conn[database_name][key_collection_name].find({"login": login})
    ]
    if keys:
        return keys


async def get_api_keys_by_journal(
    conn: AsyncIOMotorClient, login: str, journal_id: PyObjectId | str
) -> Optional[List[KeyApiInDB]]:
    try:
        keys = [
            KeyApiInDB(**key)
            async for key in conn[database_name][key_collection_name].find(
                {"login": login, "journal_id": PyObjectId(journal_id)}
            )
        ]
        if keys:
            return keys
    except bson.errors.InvalidId:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail="Not valid id of journal"
        )


async def get_api_key(
    conn: AsyncIOMotorClient, key_id: PyObjectId | str, login: str
) -> Optional[KeyApiInDB]:
    try:
        dbkey = await conn[database_name][key_collection_name].find_one(
            {"_id": PyObjectId(key_id), "login": login}
        )
        if dbkey:
            return KeyApiInDB(**dbkey)
    except bson.errors.InvalidId:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail="Not valid id of journal"
        )


async def get_api_key_by_token(
    conn: AsyncIOMotorClient, key_id: PyObjectId | str
) -> Optional[KeyApiInDB]:
    dbkey = await conn[database_name][key_collection_name].find_one({"token": key_id})
    if dbkey:
        return KeyApiInDB(**dbkey)


async def delete_api_key(
    conn: AsyncIOMotorClient, key_id: PyObjectId | str, login: str
):
    from ..crud.log import remove_logs_by_key_id

    try:
        key_db = await get_api_key(conn, PyObjectId(key_id), login)
        if key_db:
            await remove_journal_token_from_preview(conn, key_db.journal_id, key_id)

        await remove_logs_by_key_id(conn, key_id)
        del_res = await conn[database_name][key_collection_name].delete_one(
            {"_id": PyObjectId(key_id), "login": login}
        )
        if del_res.deleted_count != 1:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"Api Key with ID {key_id} not found",
            )

    except bson.errors.InvalidId:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail="Not valid id of journal"
        )


async def update_api_key(
    conn: AsyncIOMotorClient, key: KeyApiUpdate, login: str
) -> KeyApiInDB:
    dbkey = await get_api_key(conn, key.id, login)
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
        {"_id": key.id}, {"$set": dbkey.dict()}
    )

    if res.modified_count != 1:
        raise HTTPException(
            HTTP_422_UNPROCESSABLE_ENTITY, detail="Error while update api key"
        )

    return dbkey
