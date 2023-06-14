import json
import typing
from dataclasses import asdict
from dataclasses import dataclass
from enum import Enum
from json.decoder import JSONDecodeError

from fastapi import WebSocket
from fastapi import WebSocketException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic.error_wrappers import ValidationError

from ..crud.log import add_log_ws
from ..models.log import LogRequest


class ClientLogEventKind(Enum):
    PUSH_LOG = "push_log"
    PUSH_LOGS = "push_logs"
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PONG = "pong"


class ServiceLogEvent(Enum):
    ERROR = "error"
    ERROR_FORMAT = "error_format"
    PING = "ping"


@dataclass
class Msg:
    kind: str
    payload: dict

    def __str__(self):
        return f"Msg<{self.kind}>"


class BadRequestLogs(Exception):
    pass


class WSAccessor:
    """Class accessor to websocket"""

    async def connect(self, ws: WebSocket) -> WebSocket:
        """Connection to socket"""
        await ws.accept()
        print("New connect:")
        return ws

    async def send(self, ws: WebSocket, data: str):
        """Send json data"""
        await ws.send_json(data)

    async def close(self, ws: WebSocket):
        """disconnect socket"""
        await ws.close()

    async def monitor(self, connection_object: WebSocket) -> typing.AsyncIterable:
        "check stream msgs socket"
        try:
            async for message in connection_object.iter_json():
                print("MSG!", message)
                yield Msg(kind=message["kind"], payload=message["payload"])
        except JSONDecodeError as exc:
            print("EXC", exc)
            error_data = json.dumps({"error": "support json only"})
            yield Msg(kind=ServiceLogEvent.ERROR.value, payload=error_data)


class WSLogger:
    """Class of data proccesing logs"""

    async def add_log(self, msg: Msg, token: str, db: AsyncIOMotorClient) -> Msg | None:
        """Добавить лог в БД"""
        try:
            log_request = LogRequest(**msg.payload, api_key_public=token)
            await add_log_ws(db, log_request)
        except ValidationError:
            return Msg(
                kind=ServiceLogEvent.ERROR_FORMAT.value,
                payload={"error": "validation error"},
            )
        except WebSocketException as exc:
            return Msg(kind=ServiceLogEvent.ERROR.value, payload=exc.reason)


class WSManager:
    "Management events msgs socket"

    def __init__(self, ws_accessor: WSAccessor, ws_logger: WSLogger):
        self.dict_connections: dict[WebSocket, str] = {}
        self.ws_accessor = ws_accessor
        self.ws_logger = ws_logger
        self.count_errors = 0

    async def handle(
        self, connection_object: WebSocket, token: str, db: AsyncIOMotorClient
    ):
        async for msg in self.ws_accessor.monitor(connection_object):
            should_continue = await self._handle_event(
                connection_object, msg, token, db
            )
            if not should_continue:
                print("closing connection:", token)
                break

    async def _handle_event(
        self, connection_object: WebSocket, msg: Msg, token: str, db: AsyncIOMotorClient
    ) -> bool:
        if msg.kind == ClientLogEventKind.PUSH_LOG:
            msg = await self.ws_logger.add_log(msg, token, db)
            if msg is not None:
                self.count_errors += 1
                await self._send_response(connection_object, msg)
            return True
        elif msg.kind == ServiceLogEvent.ERROR:
            await self._send_response(connection_object, msg)
            return True
        else:
            raise NotImplementedError

    async def _send_response(self, connection_object: WebSocket, msg: Msg):
        if self.count_errors >= 5:
            raise BadRequestLogs("Bad requests logs multiple ")
        msg_json = json.dumps(asdict(msg))
        await self.ws_accessor.send(connection_object, msg_json)

    async def open_ws(self, connection_object: WebSocket, token: str):
        print("new handle connection with token:", token)
        ws = await self.ws_accessor.connect(connection_object)
        self.dict_connections[token] = connection_object
        print(self.dict_connections)
        return ws

    async def close_ws(self, connection_object: WebSocket):
        await self.ws_accessor.close(connection_object)

        token = [
            token
            for token in self.dict_connections.keys()
            if self.dict_connections[token] == connection_object
        ]
        if not token:
            return
        del self.dict_connections[token[0]]


class WSContext:
    def __init__(self, manager: WSManager, ws: WebSocket, token: str):
        self.manager = manager
        self.ws = ws
        self.token = token

    async def __aenter__(self) -> WebSocket:
        self.connection_object = await self.manager.open_ws(self.ws, self.token)
        return self.connection_object

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.manager.close_ws(self.ws)
        except RuntimeError as exc:
            print("Runtime error", exc)
