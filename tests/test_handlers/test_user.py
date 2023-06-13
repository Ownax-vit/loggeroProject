import pytest
from fastapi.testclient import TestClient

#
# @pytest.mark.xfail
# def rmv_user(request, test_client, test_user):
#     resp = test_client.delete()


@pytest.mark.smoke
def test_create_user(test_client: TestClient, test_user: dict):
    resp = test_client.post("/auth/sign-up", json=test_user)
    assert resp.status_code == 201
    res_data = resp.json()
    assert res_data["login"] == test_user["login"]
    assert res_data["email"] == test_user["email"]


@pytest.mark.xfail
def test_create_user_fail(test_client: TestClient, test_user_fail: dict):
    resp = test_client.post("/auth/sign-up", json=test_user_fail)
    assert resp.status_code == 201


@pytest.mark.smoke
def test_sign_in(test_client: TestClient, test_user: dict):
    resp = test_client.post("/auth/sign-up", json=test_user)
    assert resp.status_code == 201

    resp = test_client.post(
        "/auth/sign-in",
        json={"email": test_user["email"], "password": test_user["password"]},
    )
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["login"] == test_user["login"]
    assert res_data["email"] == test_user["email"]
    assert res_data["token"] is not None
