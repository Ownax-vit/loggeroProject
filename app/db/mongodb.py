
from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import MONGODB_URL

class Database:
    client: AsyncIOMotorClient = None


db = Database()


async def get_database() -> AsyncIOMotorClient:
    return db.client