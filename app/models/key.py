from datetime import datetime
from typing import List

from .base import RWModel
from .base import DBModelMixin


class KeyApi(RWModel, DBModelMixin):
    token: str
    expire: datetime


class KeyApiDelete(RWModel):
    token: str


class KeyApiCreate(RWModel):
    name: str
    description: str


class KeyApiInDB(KeyApi, KeyApiCreate):
    login: str


class KeyApiUpdate(RWModel):
    token: str | None
    name: str | None
    description: str | None


class KeyApiInResponse(KeyApiInDB):
    pass


class ListKeysInResponse(RWModel):
    keys: List[KeyApiInResponse]
