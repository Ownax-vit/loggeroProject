from typing import Optional, List
from datetime import datetime

from .base import RWModel


class KeyApi(RWModel):
    token: str
    expire: datetime


class KeyApiDelete(RWModel):
    token: str


class KeyApiCreate(RWModel):
    name: str
    description: str


class KeyApiInDB(KeyApi, KeyApiCreate):
    login: str


class KeyApiInResponse(KeyApi, KeyApiCreate):
    pass


class ListKeysInResponse(RWModel):
    keys: List[KeyApiInResponse]








