from fastapi import HTTPException
from starlette.status import HTTP_502_BAD_GATEWAY

from ..core.config import database_name
from ..core.config import users_collection_name
from ..db.mongodb import AsyncIOMotorClient
from ..models.user import UserInCreate
from ..models.user import UserInDB


async def get_user(conn: AsyncIOMotorClient, login: str) -> UserInDB | None:
    res = await conn[database_name][users_collection_name].find_one({"login": login})
    if res:
        return UserInDB(**res)


async def get_user_by_email(conn: AsyncIOMotorClient, login: str) -> UserInDB | None:
    res = await conn[database_name][users_collection_name].find_one({"login": login})
    if res:
        return UserInDB(**res)


async def create_user(conn: AsyncIOMotorClient, user: UserInCreate) -> UserInDB:
    db_user = UserInDB(**user.dict())
    db_user.change_password(user.password)

    res = await conn[database_name][users_collection_name].insert_one(
        db_user.dict(by_alias=True)
    )
    if not res:
        raise HTTPException(
            status_code=HTTP_502_BAD_GATEWAY, detail="Error create user to database"
        )

    return db_user
