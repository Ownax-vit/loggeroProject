import logging

import certifi
from motor.motor_asyncio import AsyncIOMotorClient

from .mongodb import db


async def connect_to_mongo(url_database: str):
    logging.info("Connection to Mongodb...")
    ca = certifi.where()
    try:
        db.client = AsyncIOMotorClient(
            str(url_database), serverSelectionTimeoutMS=5000, tlsCAFile=ca
        )
        print(await db.client.server_info())
        logging.info("Connected to Mongodb")
    except Exception as exc:
        print("Unable to connect to the server mongodb:\n", str(exc))


async def close_connection_mongo():
    logging.info("Closing connection Mongodb...")
    db.client.close()
    logging.info("Closed!")
