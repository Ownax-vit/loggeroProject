from typing import List

from pydantic import BaseModel
from pydantic import Field

from .base import DBModelBase
from .base import DBModelMixin
from .key import KeyApi


class Journal(DBModelMixin):
    pass


class JournalCreate(BaseModel):
    name: str = Field(...)
    description: str = Field(...)
    api_keys: List[KeyApi] | None


class JournalInDB(JournalCreate, Journal):
    user_login: str = Field(...)


class JournalInResponse(JournalInDB):
    pass


class JournalUpdate(DBModelMixin):
    name: str = Field(default=None)
    description: str = Field(default=None)
    api_keys: List[KeyApi] | None


class JournalDelete(DBModelMixin):
    pass


class ListJournalInResponse(DBModelBase):
    journals: List[JournalInResponse]
