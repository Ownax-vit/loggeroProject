from typing import Any
from typing import Generator

import pytest_asyncio
from starlette.testclient import TestClient


@pytest_asyncio.fixture(scope="session")
def test_user():
    return {
        "user": {
            "email": "test_user@test.com",
            "password": "qwerty1234",
            "login": "tester",
        }
    }


@pytest_asyncio.fixture(scope="function")
async def client() -> Generator[TestClient, Any, None]:
    from app.main import app

    with TestClient(app) as client:
        yield client
    # db = MongoClient(MONGODB_URL)
    # db[database_name][users_collection_name].delete_one({"login": test_user["user"]["login"]})
