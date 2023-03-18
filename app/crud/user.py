from pydantic import EmailStr

from ..core.config import database_name
from ..core.config import users_collection_name
from ..db.mongodb import AsyncIOMotorClient
from ..models.user import UserInCreate
from ..models.user import UserInDB


async def get_user(conn: AsyncIOMotorClient, login: str) -> UserInDB:
    row = await conn[database_name][users_collection_name].find_one({"login": login})
    if row:
        return UserInDB(**row)


async def get_user_by_email(conn: AsyncIOMotorClient, email: EmailStr) -> UserInDB:
    row = await conn[database_name][users_collection_name].find_one({"email": email})
    if row:
        return UserInDB(**row)


async def create_user(conn: AsyncIOMotorClient, user: UserInCreate) -> UserInDB:
    dbuser = UserInDB(**user.dict())
    dbuser.change_password(user.password)

    await conn[database_name][users_collection_name].insert_one(
        dbuser.dict(by_alias=True)
    )

    return dbuser
