import json

import pytest
from fastapi.testclient import TestClient


@pytest.mark.smoke
def test_ws_push_logs(
    test_client: TestClient, test_login_token: dict, created_logs_for_ws: list
):
    with test_client.websocket_connect(
        f"/ws/{created_logs_for_ws[0]['api_key_public']}"
    ) as ws:
        for log in created_logs_for_ws:
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

    test_client.get(
        f"/logs/{created_logs_for_ws[0]['api_key_id']}",
        headers=test_login_token["token"],
    )
    # TODO доделать
