from typing import List
from typing import Optional

import bson
from starlette.exceptions import HTTPException
from starlette.status import HTTP_404_NOT_FOUND
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from starlette.status import HTTP_502_BAD_GATEWAY

from ..core.config import database_name
from ..core.config import journal_collection_name
from ..db.mongodb import AsyncIOMotorClient
from ..models.base import PyObjectId
from ..models.journal import JournalCreate
from ..models.journal import JournalInDB
from ..models.journal import JournalInResponse
from ..models.journal import JournalUpdate
from ..models.key import KeyApiPreview


async def get_journal_data(
    conn: AsyncIOMotorClient, journal_id: PyObjectId | str, login: str
) -> JournalInDB | None:
    try:
        journal = await conn[database_name][journal_collection_name].find_one(
            {"_id": PyObjectId(journal_id), "login": login}
        )
        if journal:
            return JournalInDB(**journal)
    except bson.errors.InvalidId:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail="Not valid id of journal"
        )


async def create_journal_data(
    conn: AsyncIOMotorClient, journal: JournalCreate, login: str
) -> JournalInDB:
    journal_db = JournalInDB(**journal.dict(), login=login)
    res = await conn[database_name][journal_collection_name].insert_one(
        journal_db.dict(by_alias=True)
    )
    if not res:
        raise HTTPException(
            status_code=HTTP_502_BAD_GATEWAY, detail="Error insert journal to database"
        )
    return journal_db


async def update_journal_data(
    conn: AsyncIOMotorClient, journal: JournalUpdate, login: str
) -> JournalInDB:
    journal_db = await get_journal_data(conn, journal.id, login)
    if not journal_db:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Journal with current id for this user not found!",
        )
    journal.name = journal.name or journal_db.name
    journal.description = journal.description or journal_db.description
    journal.api_keys = journal.api_keys or journal_db.api_keys

    res = await conn[database_name][journal_collection_name].update_one(
        {"_id": PyObjectId(journal.id)}, {"$set": journal.dict()}
    )
    if res.modified_count != 1:
        raise HTTPException(
            HTTP_422_UNPROCESSABLE_ENTITY, detail="Error while update journal"
        )
    return JournalInDB(**journal.dict(by_alias=True))


async def push_journal_token(
    conn: AsyncIOMotorClient, journal_id: PyObjectId | str, key: KeyApiPreview
):
    try:
        res = await conn[database_name][journal_collection_name].update_one(
            {"_id": PyObjectId(journal_id)},
            {"$push": {"api_keys": {**key.dict(by_alias=True)}}},
        )
        if not res:
            raise HTTPException(
                status_code=HTTP_502_BAD_GATEWAY,
                detail="Error update api-key journal to database",
            )
    except bson.errors.InvalidId:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail="Not valid id of journal"
        )


async def remove_journal_token_from_preview(
    conn: AsyncIOMotorClient, journal_id: PyObjectId | str, key_id: PyObjectId | str
):
    try:
        res = await conn[database_name][journal_collection_name].update_one(
            {"_id": PyObjectId(journal_id)},
            {"$pull": {"api_keys": {"_id": PyObjectId(key_id)}}},
        )
        if not res:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Error update api-key journal, may be not find",
            )
    except bson.errors.InvalidId:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail="Not valid id of journal"
        )


async def delete_journal_data(
    conn: AsyncIOMotorClient, journal_id: PyObjectId | str, login: str
):
    del_res = await conn[database_name][journal_collection_name].delete_one(
        {"_id": PyObjectId(journal_id), "login": login}
    )
    if del_res.deleted_count != 1:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Journal with ID {journal_id} not found",
        )


async def get_list_journals(
    conn: AsyncIOMotorClient, login: str
) -> Optional[List[JournalInResponse]]:
    journal_group = [
        JournalInDB(**key)
        async for key in conn[database_name][journal_collection_name].find(
            {"login": login}
        )
    ]
    if journal_group:
        return journal_group
