import logging

from motor.motor_asyncio import AsyncIOMotorClient


class Database:
    client: AsyncIOMotorClient


db = Database()


async def get_database() -> AsyncIOMotorClient:
    return db.client