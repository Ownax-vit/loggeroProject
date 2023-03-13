import asyncio
from typing import Any, Generator

import pytest_asyncio
from starlette.testclient import TestClient
from pymongo import MongoClient

from app.db.mongodb import get_database
from app.core.config import database_name, users_collection_name, key_collection_name, MONGODB_URL


@pytest_asyncio.fixture(scope="session")
def test_user():
    return {
        "user": {
            "email": "test_user@test.com",
            "password": "qwerty1234",
            "login": "tester"
        }
    }


@pytest_asyncio.fixture(scope="function")
async def client() -> Generator[TestClient, Any, None]:
    from app.main import app

    with TestClient(app) as client:
        yield client
    # db = MongoClient(MONGODB_URL)
    # db[database_name][users_collection_name].delete_one({"login": test_user["user"]["login"]})