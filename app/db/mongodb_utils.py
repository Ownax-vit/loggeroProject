import logging

from motor.motor_asyncio import AsyncIOMotorClient

from .mongodb import db


async def connect_to_mongo():
    logging.info("Connection to Mongodb...")
    db.client = AsyncIOMotorClient()
    logging.info("Connected to Mongodb")


async def close_connection_mongo():
    logging.info("Closing connection Mongodb...")
    db.client.close()
    logging.info("Closed!")