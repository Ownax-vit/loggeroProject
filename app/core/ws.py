import json
import typing
from dataclasses import asdict
from dataclasses import dataclass
from json.decoder import JSONDecodeError

from fastapi import WebSocket
from fastapi import WebSocketException
from motor.motor_asyncio import AsyncIOMotorClient

from ..crud.log import add_log
from ..models.log import LogRequest


class ClientLogEventKind:
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PING = "ping"
    ERROR = "error"


class ServiceLogEvent:
    PUSH_LOG = "push_log"
    PUSH_LOGS = "push_logs"


@dataclass
class Msg:
    kind: str
    payload: dict

    def __str__(self):
        return f"Msg<{self.kind}>"


class WSAccessor:
    """Сокет адаптер"""

    async def connect(self, ws: WebSocket) -> WebSocket:
        """Установка коннекта"""
        await ws.accept()
        print("New connect:")
        return ws
        # self._push(token, ws)

    async def push(self, ws: WebSocket, data: str):
        """Отправка данных в json"""
        await ws.send_json(data)

    async def close(self, connection_id: int):
        """закрытие соединения"""
        await connection_id.close()

    async def monitor(self, connection_object: WebSocket) -> typing.AsyncIterable:
        try:
            async for message in connection_object.iter_json():
                print(message)
                yield Msg(kind=message["kind"], payload=message["payload"])
        except JSONDecodeError as exc:
            print("EXC", exc)
            error_data = json.dumps({"error": "support json only"})
            yield Msg(kind=ClientLogEventKind.ERROR, payload=error_data)


class WSManager:
    def __init__(self, ws_accessor: WSAccessor):
        self.dict_connections: dict[str, WebSocket] = {}
        self.ws_accessor = ws_accessor

    async def handle(
        self, connection_object: WebSocket, token: str, db: AsyncIOMotorClient
    ):
        print("new handle connection with token:", token)
        self.dict_connections[token] = connection_object
        async for msg in self.ws_accessor.monitor(connection_object):
            try:
                should_continue = await self._handle_event(
                    connection_object, msg, token, db
                )
                if not should_continue:
                    del self.dict_connections[token]
                    break
            except WebSocketException as exc:
                print("EXCEPTION_____", exc.reason, exc.code)

    async def _handle_event(
        self, connection_object: WebSocket, msg: Msg, token: str, db: AsyncIOMotorClient
    ) -> bool:
        if msg.kind == ServiceLogEvent.PUSH_LOG:
            print("data process msg", msg)
            log_request = LogRequest(**msg.payload, api_key_public=token)
            print(log_request)
            log = await add_log(db, log_request)
            print("Log added: ", log)
            return True
        elif msg.kind == ClientLogEventKind.ERROR:
            print("Error JSON format")
            await self._send_error(connection_object, msg)
            return True
        else:
            raise NotImplementedError

    async def _send_error(self, connection_object: WebSocket, msg_error: str):
        error = json.dumps(asdict(msg_error))
        await self.ws_accessor.push(connection_object, error)


class WSContext:
    def __init__(self, manager: WSManager, ws: WebSocket):
        self.manager = manager
        self.ws = ws

    async def __aenter__(self) -> str:
        self.connection_object = await self.manager.ws_accessor.connect(self.ws)
        return self.connection_object

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.manager.ws_accessor.close(self.ws)
