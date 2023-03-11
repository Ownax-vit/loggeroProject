

from ..db.mongodb import AsyncIOMotorClient
from ..models.key import KeyApiCreate, KeyApiInDB
from ..core.config import database_name, key_collection_name


async def add_key(conn: AsyncIOMotorClient, key: KeyApiCreate, login: str) -> KeyApiInDB:
    print("key", key)
    token = "asdhfgfdsa"
    dbkey = KeyApiInDB(**key.dict(), login=login, token=token)

    row = await conn[database_name][key_collection_name].insert_one(dbkey.dict())

    return dbkey