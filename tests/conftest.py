import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def test_user():
    return {
        "email": "test_user@test.com",
        "password": "qwerty1234",
        "login": "tester",
    }


@pytest.fixture(scope="session")
def test_user_fail():
    return {
        "email": "test_user_Fail/test.com",
        "password": 123,
        "login": "tester_Fail",
    }


@pytest.fixture(scope="session")
def test_access_token(request):
    token = request.config.cache.get("access_token", None)
    return {"Authorization": f"Bearer {token}"}


# TODO решить проблему с очисткой данных
@pytest.fixture(scope="session")
def test_client():
    with TestClient(app) as client:
        yield client
