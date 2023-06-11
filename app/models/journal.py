from typing import List

from pydantic import BaseModel
from pydantic import Field

from .base import DBModelBase
from .base import DBModelMixin
from .key import KeyApiPreview


class Journal(DBModelMixin):
    pass


class JournalCreate(BaseModel):
    name: str = Field(...)
    description: str = Field(...)


class JournalInDB(JournalCreate, Journal):
    login: str = Field(...)
    api_keys: List[KeyApiPreview] | None


class JournalInResponse(JournalInDB):
    pass


class JournalUpdate(DBModelMixin):
    name: str = Field(default=None)
    description: str = Field(default=None)
    api_keys: List[KeyApiPreview] | None


class JournalDelete(DBModelMixin):
    pass


class ListJournalInResponse(DBModelBase):
    journals: List[JournalInResponse]
