from .base import DBModelBase


class TokenPayload(DBModelBase):
    login: str = ""

    class Config:
        arbitrary_types_allowed = True
