from dataclasses import dataclass

from fastapi.websockets import WebSocket


@dataclass
class ConnectionMachine:
    session: WebSocket
    token: str
