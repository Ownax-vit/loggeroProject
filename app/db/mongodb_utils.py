import sys
import logging

from starlette.exceptions import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from .mongodb import db
from ..core.config import MONGODB_URL


async def connect_to_mongo():
    logging.info("Connection to Mongodb...")
    db.client = AsyncIOMotorClient(str(MONGODB_URL), serverSelectionTimeoutMS=5000)
    try:
        print(await db.client.server_info())
        logging.info("Connected to Mongodb")
    except Exception as exc:
        print("Unable to connect to the server mongodb:\n", str(exc))


async def close_connection_mongo():
    logging.info("Closing connection Mongodb...")
    db.client.close()
    logging.info("Closed!")