from typing import List

from pydantic import BaseModel
from pydantic import Field

from .base import DBModelMixin
from .base import PyObjectId
from .key import KeyApi


class Journal(DBModelMixin):
    name: str = Field(...)
    description: str = Field(...)
    api_keys: List[KeyApi] | None


class JournalInDB(Journal):
    user: PyObjectId = Field(alias="user_id")


class JournalInResponse(JournalInDB):
    pass


class JournalUpdate(DBModelMixin):
    name: str = Field(default=None)
    description: str = Field(default=None)
    api_keys: List[KeyApi] | None


class JournalDelete(DBModelMixin):
    pass


class ListJournalInResponse(BaseModel):
    journals: List[JournalInResponse]
