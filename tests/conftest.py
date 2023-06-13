import uuid
from datetime import datetime
from datetime import timedelta
from typing import Generator

import certifi
import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient

from app.core.config import API_KEY_EXPIRE_DAYS
from app.core.config import database_name
from app.core.config import journal_collection_name
from app.core.config import key_collection_name
from app.core.config import MONGODB_URL
from app.core.config import users_collection_name
from app.main import app


TESTER_ADMIN = {
    "email": "tester_admin@test.com",
    "password": "qwerty123456",
    "login": "tester_admin",
}


@pytest.fixture(scope="session")
def mongo_db() -> Generator[MongoClient, None, None]:
    ca = certifi.where()
    client = MongoClient(str(MONGODB_URL), tlsCAFile=ca)
    yield client[database_name]


@pytest.fixture()
def test_journal():
    journal_data = {
        "name": "test journal",
        "description": "description for test journal",
    }
    return journal_data


@pytest.fixture()
def test_journal_upd():
    return {
        "name": "test journal updated data",
        "description": "description for test journal updated",
    }


@pytest.fixture(scope="function")
def test_key(created_journal: dict):

    key_data = {
        "name": "test key",
        "description": "test description key",
        "journal_id": created_journal["_id"],
    }
    return key_data


@pytest.fixture(scope="function")
def test_key_upd():
    key_data = {
        "name": "test key updated",
        "description": "test description key updated",
    }
    return key_data


@pytest.fixture(scope="function")
def test_user(mongo_db: MongoClient):
    user_data = {
        "email": "test_user@test.com",
        "password": "qwerty1234",
        "login": "tester",
    }
    yield user_data
    collection = mongo_db[users_collection_name]
    collection.delete_one({"login": user_data["login"]})


@pytest.fixture(scope="function")
def test_user_fail():
    user_data = {
        "email": "test_user_Fail/test.com",
        "password": "",
        "login": "tester_Fail",
    }
    yield user_data
    collection = mongo_db[users_collection_name]
    collection.delete_one({"login": user_data["login"]})


@pytest.fixture(scope="session")
def test_login_token(request):
    token = request.config.cache.get("access_token", None)
    login = request.config.cache.get("login", None)
    return {"login": login, "token": {"Authorization": f"Bearer {token}"}}


# TODO решить проблему с очисткой данных
@pytest.fixture(scope="session")
def test_client(request, mongo_db: MongoClient) -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        resp = client.post("/auth/sign-up", json=TESTER_ADMIN)
        data = resp.json()
        request.config.cache.set("access_token", data["token"])
        request.config.cache.set("login", data["login"])

        yield client

        collection_user = mongo_db[users_collection_name]
        collection_journal = mongo_db[journal_collection_name]
        collection_keys = mongo_db[key_collection_name]

        collection_user.delete_one({"login": data["login"]})
        collection_journal.delete_many({"login": data["login"]})
        collection_keys.delete_many({"login": data["login"]})

        request.config.cache.set("login", None)
        request.config.cache.set("access_token", None)


@pytest.fixture(scope="function")
def created_journal(
    mongo_db: MongoClient, test_journal: dict
) -> Generator[str, None, None]:
    collection = mongo_db[journal_collection_name]
    data_journal = {**test_journal, "login": TESTER_ADMIN["login"]}
    journal_id = collection.insert_one(data_journal).inserted_id
    data_journal["_id"] = str(journal_id)
    yield data_journal
    collection.delete_one({"_id": journal_id})


@pytest.fixture(scope="function")
def created_key(mongo_db: MongoClient, test_key: dict):
    collection = mongo_db[key_collection_name]
    token = str(uuid.uuid4())
    expire = datetime.utcnow() + timedelta(API_KEY_EXPIRE_DAYS)
    data_key = {
        **test_key,
        "login": TESTER_ADMIN["login"],
        "expire": expire,
        "token": token,
    }
    key_id = collection.insert_one(data_key).inserted_id
    data_key["_id"] = str(key_id)
    yield data_key
    collection.delete_one({"_id": key_id})
