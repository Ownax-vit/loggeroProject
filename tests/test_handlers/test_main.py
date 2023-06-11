def test_ping(test_client):
    resp = test_client.get("/ping_test")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Hello world"}
