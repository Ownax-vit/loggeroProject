from datetime import datetime
from datetime import timedelta
from datetime import timezone

import pytest
from fastapi.testclient import TestClient

from app.core.config import API_KEY_EXPIRE_DAYS


@pytest.mark.smoke
def test_key_create(test_client: TestClient, test_login_token: dict, test_key: dict):
    resp = test_client.post(
        "/api-key/key", headers=test_login_token["token"], json=test_key
    )
    assert resp.status_code == 201
    resp_key = resp.json()
    assert resp_key["name"] == test_key["name"]
    assert resp_key["description"] == test_key["description"]
    assert resp_key["journal_id"] == test_key["journal_id"]
    assert resp_key["login"] == test_login_token["login"]

    assert datetime.fromisoformat(resp_key["expire"]) < datetime.now(
        timezone.utc
    ) + timedelta(API_KEY_EXPIRE_DAYS)
    assert datetime.fromisoformat(resp_key["expire"]) > datetime.now(
        timezone.utc
    ) + timedelta(API_KEY_EXPIRE_DAYS - 1)

    # check token in journal
    resp_journal = test_client.get(
        f"/journal/{test_key['journal_id']}", headers=test_login_token["token"]
    )
    resp_journal_data = resp_journal.json()
    assert resp_journal.status_code == 200
    assert resp_key["token"] in [key["token"] for key in resp_journal_data["api_keys"]]


@pytest.mark.smoke
def test_key_get(test_client: TestClient, test_login_token: dict, created_key: dict):
    resp = test_client.get(
        f"/api-key/key/{created_key['_id']}", headers=test_login_token["token"]
    )
    assert resp.status_code == 200
    resp_key = resp.json()
    assert resp_key["_id"] == created_key["_id"]
    assert resp_key["journal_id"] == created_key["journal_id"]
    assert resp_key["name"] == created_key["name"]
    assert resp_key["description"] == created_key["description"]
    assert resp_key["login"] == created_key["login"]

    assert datetime.fromisoformat(resp_key["expire"]).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    ) == created_key["expire"].strftime("%Y-%m-%dT%H:%M:%SZ")
    assert resp_key["token"] == created_key["token"]


@pytest.mark.smoke
def test_key_delete(test_client: TestClient, test_login_token: dict, created_key: dict):
    resp = test_client.delete(
        f"/api-key/key/{created_key['_id']}", headers=test_login_token["token"]
    )
    assert resp.status_code == 204

    new_resp = test_client.get(
        f"/api-key/key{created_key['_id']}", headers=test_login_token["token"]
    )
    assert new_resp.status_code == 404


@pytest.mark.smoke
def test_key_update(
    test_client: TestClient,
    test_login_token: dict,
    created_key: dict,
    test_key_upd: dict,
):
    resp = test_client.put(
        "/api-key/key",
        json={**test_key_upd, "_id": created_key["_id"]},
        headers=test_login_token["token"],
    )
    assert resp.status_code == 200
    resp_key = resp.json()
    assert resp_key["name"] != created_key["name"]
    assert resp_key["description"] != created_key["description"]


@pytest.mark.smoke
def test_keys_get(test_client: TestClient, test_login_token: dict, created_key: dict):
    resp = test_client.get("/api-key/keys", headers=test_login_token["token"])
    assert resp.status_code == 200
    resp_keys = resp.json()
    assert len(resp_keys) != 0
    for key in resp_keys["keys"]:
        assert key["login"] == test_login_token["login"]
