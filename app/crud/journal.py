from ..core.config import database_name
from ..core.config import journal_collection_name
from ..db.mongodb import AsyncIOMotorClient
from ..models.journal import Journal
from ..models.journal import JournalInResponse


async def create_journal(
    conn: AsyncIOMotorClient, journal: Journal, login: str
) -> JournalInResponse:
    await conn[database_name][journal_collection_name].insert_one(
        journal.dict(), user=login
    )
