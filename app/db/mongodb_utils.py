import logging

from motor.motor_asyncio import AsyncIOMotorClient

from .mongodb import db
from ..core.config import MONGODB_URL


async def connect_to_mongo():
    logging.info("Connection to Mongodb...")
    db.client = AsyncIOMotorClient(str(MONGODB_URL))
    logging.info("Connected to Mongodb")


async def close_connection_mongo():
    logging.info("Closing connection Mongodb...")
    db.client.close()
    logging.info("Closed!")