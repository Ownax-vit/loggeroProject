import json
import time
from datetime import datetime

import pytest
from fastapi.testclient import TestClient


@pytest.mark.smoke
def test_ws_push_logs(
    test_client: TestClient, test_login_token: dict, logs_for_ws: list
):
    with test_client.websocket_connect(f"/ws/{logs_for_ws[0]['api_key_public']}") as ws:
        for log in logs_for_ws:
            ws.send_json(
                json.dumps(
                    {
                        "kind": "push_log",
                        "payload": {
                            "name": log["name"],
                            "type": log["type"],
                            "date": log["date"],
                        },
                    }
                )
            )
            time.sleep(0.5)

    resp = test_client.get(
        f"/logs/{logs_for_ws[0]['api_key_id']}",
        headers=test_login_token["token"],
    )

    resp_logs = resp.json()["logs"]
    assert len(resp_logs) == len(logs_for_ws)
    sorted_logs = sorted(resp_logs, key=lambda log_el: log_el["date"])
    for index, log in enumerate(sorted_logs):
        assert log["name"] == logs_for_ws[index]["name"]
        assert log["type"] == logs_for_ws[index]["type"]
        assert datetime.fromisoformat(log["date"]).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ) == datetime.fromisoformat(logs_for_ws[index]["date"]).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
