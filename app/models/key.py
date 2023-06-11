from datetime import datetime
from typing import List

from pydantic import Field

from .base import DBModelBase
from .base import DBModelMixin
from .base import PyObjectId


class KeyApi(DBModelBase, DBModelMixin):
    token: str
    expire: datetime


class KeyApiPreview(KeyApi):
    name: str


class KeyApiDelete(DBModelMixin):
    pass


class KeyApiCreate(DBModelBase):
    name: str
    description: str
    journal_id: PyObjectId = Field()


class KeyApiInDB(KeyApi, KeyApiCreate):
    login: str


class KeyApiUpdate(DBModelBase, DBModelMixin):
    name: str | None
    description: str | None


class KeyApiInResponse(KeyApiInDB):
    pass


class ListKeysInResponse(DBModelBase):
    keys: List[KeyApiInResponse]
