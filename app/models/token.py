from .base import RWModel


class TokenPayload(RWModel):
    login: str = ""
