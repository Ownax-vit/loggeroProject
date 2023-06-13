import pytest
from fastapi.testclient import TestClient


@pytest.mark.smoke
def test_journal_delete(
    test_client: TestClient,
    test_login_token: dict,
    created_journal: dict,
):
    resp = test_client.delete(
        f"/journal/{created_journal['_id']}", headers=test_login_token["token"]
    )
    assert resp.status_code == 204

    new_resp = test_client.get(
        f"/journal/{created_journal['_id']}", headers=test_login_token["token"]
    )
    assert new_resp.status_code == 404


@pytest.mark.smoke
def test_journal_create(
    test_client: TestClient, test_login_token: dict, test_journal: dict
):
    resp = test_client.post(
        "/journal", headers=test_login_token["token"], json=test_journal
    )
    assert resp.status_code == 201
    journal_data = resp.json()
    assert journal_data["name"] == test_journal["name"]
    assert journal_data["description"] == test_journal["description"]
    assert journal_data["login"] == test_login_token["login"]


@pytest.mark.smoke
def test_journal_get(
    test_client: TestClient,
    test_login_token: dict,
    created_journal: dict,
):
    resp = test_client.get(
        f"/journal/{created_journal['_id']}", headers=test_login_token["token"]
    )
    assert resp.status_code == 200
    journal_data_get = resp.json()

    assert journal_data_get["_id"] == created_journal["_id"]
    assert journal_data_get["name"] == created_journal["name"]
    assert journal_data_get["description"] == created_journal["description"]
    assert journal_data_get["login"] == test_login_token["login"]


@pytest.mark.smoke
def test_journal_put(
    test_client: TestClient,
    test_login_token: dict,
    test_journal_upd: dict,
    created_journal: dict,
):
    resp = test_client.put(
        "/journal",
        headers=test_login_token["token"],
        json={"_id": created_journal["_id"], **test_journal_upd},
    )
    assert resp.status_code == 200
    journal_data_get = resp.json()

    assert journal_data_get["name"] != created_journal["name"]
    assert journal_data_get["description"] != created_journal["description"]

    assert journal_data_get["name"] == test_journal_upd["name"]
    assert journal_data_get["description"] == test_journal_upd["description"]
    assert journal_data_get["login"] == test_login_token["login"]


@pytest.mark.smoke
def test_journals_get(test_client: TestClient, test_login_token: dict):
    resp = test_client.get("/journals", headers=test_login_token["token"])
    assert resp.status_code == 200
    journal_data_get = resp.json()
    assert len(journal_data_get) != 0
    for journal in journal_data_get["journals"]:
        assert journal["login"] == test_login_token["login"]
