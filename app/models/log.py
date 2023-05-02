from datetime import datetime
from typing import List

from pydantic import Field

from .base import DBModelBase
from .base import DBModelMixin
from .base import PyObjectId


class LogBase(DBModelBase):
    name: str = Field(...)
    type: str = Field(default="Log")
    date: datetime


class LogRequest(LogBase):
    api_key_public: str = Field(...) # token == key-api публичный ид токена uuid строка


class LogInDb(LogBase, DBModelMixin):
    api_key_id: PyObjectId = Field(...) #  PyObject - уникальный ид токена хэш в монго


class ListLogRequest(DBModelBase):
    api_key_id: PyObjectId = Field(...) # PyObject - уникальный ид токена


class ListLogsShow(DBModelBase):
    logs: List[LogInDb]


