from datetime import datetime

import pytest
from fastapi.testclient import TestClient


@pytest.mark.smoke
def test_log_create(test_client: TestClient, test_login_token: dict, test_log: dict):
    resp = test_client.post("/log", headers=test_login_token["token"], json=test_log)
    assert resp.status_code == 201
    resp_key = resp.json()
    assert resp_key["name"] == test_log["name"]
    assert resp_key["type"] == test_log["type"]
    assert datetime.fromisoformat(resp_key["date"]).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    ) == datetime.fromisoformat(test_log["date"]).strftime("%Y-%m-%dT%H:%M:%SZ")


@pytest.mark.smoke
def test_log_create_failed_expire(
    test_client: TestClient, test_login_token: dict, test_log_failed_datetime: dict
):
    resp = test_client.post(
        "/log", headers=test_login_token["token"], json=test_log_failed_datetime
    )
    assert resp.status_code == 410
    assert resp.json()["detail"] == "Current token expired!"


@pytest.mark.smoke
def test_log_create_failed_token(
    test_client: TestClient, test_login_token: dict, test_log_failed_token: dict
):
    resp = test_client.post(
        "/log", headers=test_login_token["token"], json=test_log_failed_token
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Current api-key not found!"


@pytest.mark.smoke
def test_logs_get(test_client: TestClient, test_login_token: dict, created_log: dict):
    resp = test_client.get(
        f"/logs/{created_log['api_key_id']}", headers=test_login_token["token"]
    )
    assert resp.status_code == 200
    assert len(resp.json()) != 0
