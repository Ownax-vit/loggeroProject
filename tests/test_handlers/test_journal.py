import pytest
from fastapi.testclient import TestClient


@pytest.mark.smoke
def test_journal_delete(
    test_client: TestClient, test_login_token: dict, create_journal_id
):
    resp = test_client.delete(
        f"/journal/{create_journal_id}", headers=test_login_token["token"]
    )
    assert resp.status_code == 204


@pytest.mark.smoke
def test_journal_create(test_client: TestClient, test_login_token: dict, test_journal):
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
    test_journal: dict,
    create_journal_id,
):
    resp = test_client.get(
        f"/journal/{create_journal_id}", headers=test_login_token["token"]
    )
    assert resp.status_code == 200
    journal_data_get = resp.json()

    if journal_data_get["api_keys"] is not None:
        for key in journal_data_get.keys():
            assert journal_data_get[key] == create_journal_id[key]

    assert journal_data_get["_id"] == str(create_journal_id)
    assert journal_data_get["name"] == test_journal["name"]
    assert journal_data_get["description"] == test_journal["description"]
    assert journal_data_get["login"] == test_login_token["login"]


@pytest.mark.smoke
def test_journal_put(
    test_client: TestClient,
    test_login_token: dict,
    test_journal: dict,
    test_journal_upd: dict,
    create_journal_id,
):
    resp = test_client.put(
        "/journal",
        headers=test_login_token["token"],
        json={"_id": create_journal_id, **test_journal_upd},
    )
    assert resp.status_code == 200
    journal_data_get = resp.json()

    assert journal_data_get["name"] != test_journal["name"]
    assert journal_data_get["description"] != test_journal["description"]

    assert journal_data_get["name"] == test_journal_upd["name"]
    assert journal_data_get["description"] == test_journal_upd["description"]
    assert journal_data_get["login"] == test_login_token["login"]


@pytest.mark.smoke
def test_journals_get(
    test_client: TestClient, test_login_token: dict, create_journal_id
):
    resp = test_client.get("/journals", headers=test_login_token["token"])
    assert resp.status_code == 200
    journal_data_get = resp.json()
    assert len(journal_data_get) != 0
    for journal in journal_data_get["journals"]:
        assert journal["login"] == test_login_token["login"]
