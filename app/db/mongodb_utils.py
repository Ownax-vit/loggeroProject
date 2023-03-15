import logging

import certifi
from motor.motor_asyncio import AsyncIOMotorClient

from ..core.config import MONGODB_URL
from .mongodb import db


async def connect_to_mongo():
    logging.info("Connection to Mongodb...")
    ca = certifi.where()
    db.client = AsyncIOMotorClient(str(MONGODB_URL), serverSelectionTimeoutMS=5000, tlsCAFile=ca)
    try:
        print(await db.client.server_info())
        logging.info("Connected to Mongodb")
    except Exception as exc:
        print("Unable to connect to the server mongodb:\n", str(exc))


async def close_connection_mongo():
    logging.info("Closing connection Mongodb...")
    db.client.close()
    logging.info("Closed!")
