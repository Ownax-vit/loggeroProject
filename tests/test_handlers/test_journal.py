import pytest


@pytest.fixture()
def test_journal():
    return {
        "name": "test journal",
        "description": "description for test journal",
    }


@pytest.mark.smoke
def test_get_journals(test_client, test_access_token):
    resp = test_client.get("/journals", headers=test_access_token)
    assert resp.status_code == 404


@pytest.mark.smoke
def test_create_journal(test_client, test_access_token, test_journal):
    resp = test_client.post("/journal", headers=test_access_token, json=test_journal)
    assert resp.status_code == 201
    journal_data = resp.json()
    assert journal_data["name"] == test_journal["name"]
    assert journal_data["description"] == test_journal["description"]
