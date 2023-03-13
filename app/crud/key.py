import uuid
from datetime import timedelta, datetime
from typing import Optional, List

from ..db.mongodb import AsyncIOMotorClient
from ..models.key import KeyApiCreate, KeyApiInDB, KeyApiInResponse, ListKeysInResponse
from ..core.config import database_name, key_collection_name, API_KEY_EXPIRE_DAYS


async def add_api_key(conn: AsyncIOMotorClient, key: KeyApiCreate, login: str) -> KeyApiInDB:
    token = str(uuid.uuid4())
    expire = datetime.utcnow() + timedelta(API_KEY_EXPIRE_DAYS)
    dbkey = KeyApiInDB(**key.dict(), login=login, token=token, expire=expire)

    await conn[database_name][key_collection_name].insert_one(dbkey.dict())

    return dbkey


async def get_api_keys(conn: AsyncIOMotorClient, login: str) -> Optional[List[KeyApiInResponse]]:
    keys = [KeyApiInResponse(**key) async for key in conn[database_name][key_collection_name].find({"login": login})]
    return keys


async def delete_api_key(conn: AsyncIOMotorClient, key: str):
    print(key)
    await conn[database_name][key_collection_name].delete_one({'token': key})

