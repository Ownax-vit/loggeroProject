import pytest

@pytest.mark.asyncio
async def test_create_user(client, test_user):
    resp = client.post("auth/sign-up", json=test_user)
    print(resp.json)
    data_resp = resp.json()["user"]
    assert resp.status_code == 201
    assert data_resp["login"] == "tester"