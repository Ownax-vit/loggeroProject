from datetime import datetime
from typing import List

from .base import DBModelBase
from .base import DBModelMixin


class KeyApi(DBModelBase, DBModelMixin):
    token: str
    expire: datetime


class KeyApiDelete(DBModelMixin):
    pass


class KeyApiCreate(DBModelBase):
    name: str
    description: str


class KeyApiInDB(KeyApi, KeyApiCreate):
    login: str


class KeyApiUpdate(DBModelBase, DBModelMixin):
    name: str | None
    description: str | None


class KeyApiInResponse(KeyApiInDB):
    pass


class ListKeysInResponse(DBModelBase):
    keys: List[KeyApiInResponse]
