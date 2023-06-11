import pytest


@pytest.mark.smoke
def test_create_user(request, test_client, test_user):
    resp = test_client.post("/auth/sign-up", json=test_user)
    res_data = resp.json()
    assert resp.status_code == 201
    assert res_data == test_user
    request.config.cache.set("access_token", res_data["token"])


@pytest.mark.xfail
def test_create_user_fail(test_client, test_user_fail):
    resp = test_client.post("/auth/sign-up", json=test_user_fail)
    assert resp.status_code == 201
    assert resp.json() == test_user_fail


@pytest.mark.smoke
def test_sign_in(request, test_client, test_user):
    resp = test_client.post(
        "/auth/sign-in",
        json={"email": test_user["email"], "password": test_user["password"]},
    )
    res_data = resp.json()
    assert resp.status_code == 201
    assert res_data["login"] == test_user["login"]
    assert res_data["email"] == test_user["email"]
    request.config.cache.set("access_token", res_data["token"])
