import json
import typing
from dataclasses import asdict
from dataclasses import dataclass
from json.decoder import JSONDecodeError

from fastapi import WebSocket
from fastapi import WebSocketException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic.error_wrappers import ValidationError

from ..crud.log import add_log
from ..models.log import LogRequest


class ClientLogEventKind:
    PUSH_LOG = "push_log"
    PUSH_LOGS = "push_logs"
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PONG = "pong"


class ServiceLogEvent:
    ERROR = "error"
    ERROR_FORMAT = "error_format"
    PING = "ping"


@dataclass
class Msg:
    kind: str
    payload: dict

    def __str__(self):
        return f"Msg<{self.kind}>"


class WSAccessor:
    """Class accessor to websocket"""

    async def connect(self, ws: WebSocket) -> WebSocket:
        """Connection to socket"""
        await ws.accept()
        print("New connect:")
        return ws

    async def push(self, ws: WebSocket, data: str):
        """Send json data"""
        await ws.send_json(data)

    async def close(self, connection_id: int):
        """disconnect socket"""
        await connection_id.close()

    async def monitor(self, connection_object: WebSocket) -> typing.AsyncIterable:
        "check stream msgs socket"
        try:
            async for message in connection_object.iter_json():
                print(message)
                yield Msg(kind=message["kind"], payload=message["payload"])
        except JSONDecodeError as exc:
            print("EXC", exc)
            error_data = json.dumps({"error": "support json only"})
            yield Msg(kind=ServiceLogEvent.ERROR, payload=error_data)


class WSLogger:
    """Class of data proccesing logs"""

    async def add_log(self, msg: Msg, token: str, db: AsyncIOMotorClient) -> Msg | None:
        """Добавить лог в БД"""
        try:
            log_request = LogRequest(**msg.payload, api_key_public=token)
            await add_log(db, log_request)
        except ValidationError as exc:
            return Msg(kind=ServiceLogEvent.ERROR_FORMAT, payload=exc)
        except WebSocketException as exc:
            return Msg(kind=ServiceLogEvent.ERROR, payload=exc.reason)


class WSManager:
    "Management events msgs socket"

    def __init__(self, ws_accessor: WSAccessor, ws_logger: WSLogger):
        self.dict_connections: dict[str, WebSocket] = {}
        self.ws_accessor = ws_accessor
        self.ws_logger = ws_logger

    async def handle(
        self, connection_object: WebSocket, token: str, db: AsyncIOMotorClient
    ):
        print("new handle connection with token:", token)
        self.dict_connections[token] = connection_object
        async for msg in self.ws_accessor.monitor(connection_object):
            should_continue = await self._handle_event(
                connection_object, msg, token, db
            )
            if not should_continue:
                del self.dict_connections[token]
                break

    async def _handle_event(
        self, connection_object: WebSocket, msg: Msg, token: str, db: AsyncIOMotorClient
    ) -> bool:
        if msg.kind == ClientLogEventKind.PUSH_LOG:
            msg = await self.ws_logger.add_log(msg, token, db)
            if msg is not None:
                self._send_response(connection_object, msg)
            return True
        elif msg.kind == ServiceLogEvent.ERROR:
            await self._send_response(connection_object, msg)
            return True
        else:
            raise NotImplementedError

    async def _send_response(self, connection_object: WebSocket, msg: str):
        msg_json = json.dumps(asdict(msg))
        await self.ws_accessor.push(connection_object, msg_json)


class WSContext:
    def __init__(self, manager: WSManager, ws: WebSocket):
        self.manager = manager
        self.ws = ws

    async def __aenter__(self) -> str:
        self.connection_object = await self.manager.ws_accessor.connect(self.ws)
        return self.connection_object

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.manager.ws_accessor.close(self.ws)
        except RuntimeError as exc:
            print("Runtime error", exc)
