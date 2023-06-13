import pytest
from fastapi.testclient import TestClient

FAKE_JWT = (
    "eyJhbGciOiJIUzI1NiJ9.eyJTdWIiOiJBY2Nlc3MiLC"
    "JMb2dpbiI6InRlc3Rlcl9hZG1pbiIsIkV4cCI6IjE2ODY0MDM3MjMwMDAifQ.-t-wC-WlDiBoqQMYdgIT-kHDar9yztvtNlX73lCY6kg"
)


@pytest.mark.smoke
def test_ping(test_client: TestClient):
    resp = test_client.get("/ping_test")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Hello world"}


@pytest.mark.smoke
def test_empty_access_token(test_client: TestClient):
    resp = test_client.get("/journals")
    assert resp.status_code == 422


@pytest.mark.smoke
def test_fail_access_token(test_client: TestClient):
    resp = test_client.get("/journals", headers={"Authorization": f"Bearer {FAKE_JWT}"})
    assert resp.status_code == 401
