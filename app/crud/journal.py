from typing import List
from typing import Optional

from bson import ObjectId
from starlette.exceptions import HTTPException
from starlette.status import HTTP_404_NOT_FOUND
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from ..core.config import database_name
from ..core.config import journal_collection_name
from ..db.mongodb import AsyncIOMotorClient
from ..models.journal import JournalCreate
from ..models.journal import JournalInDB
from ..models.journal import JournalInResponse
from ..models.journal import JournalUpdate


async def get_journal_data(
    conn: AsyncIOMotorClient, journal_id: str, login: str
) -> JournalInDB:
    journal = await conn[database_name][journal_collection_name].find_one(
        {"_id": ObjectId(journal_id), "user_login": login}
    )
    if journal:
        return JournalInDB(**journal)


async def create_journal_data(
    conn: AsyncIOMotorClient, journal: JournalCreate, login: str
) -> JournalInDB:
    journaldb = JournalInDB(**journal.dict(), user_login=login)
    await conn[database_name][journal_collection_name].insert_one(
        journaldb.dict(by_alias=True)
    )
    return journaldb


async def update_journal_data(
    conn: AsyncIOMotorClient, journal: JournalUpdate
) -> JournalInDB:
    journaldb = await get_journal_data(conn, journal.id)
    # исправить
    if not journaldb:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Journal not found!")
    journal.name = journal.name or journaldb.name
    journal.description = journal.description or journaldb.description
    journal.api_keys = journal.api_keys or journaldb.api_keys

    res = await conn[database_name][journal_collection_name].update_one(
        {"_id": ObjectId(journal.id)}, {"$set": journal.dict()}
    )
    if res.modified_count != 1:
        raise HTTPException(
            HTTP_422_UNPROCESSABLE_ENTITY, detail="Error while update journal"
        )
    return JournalInDB(**journal.dict(by_alias=True))


async def delete_journal_data(conn: AsyncIOMotorClient, journal_id: str, login: str):
    del_res = await conn[database_name][journal_collection_name].delete_one(
        {"_id": ObjectId(journal_id), "user_login": login}
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
            {"user_login": login}
        )
    ]
    if journal_group:
        return journal_group
