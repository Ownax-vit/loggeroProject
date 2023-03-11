from pydantic import Field, BaseModel

from .base import RWModel


class KeyApi(BaseModel):
    token: str


class KeyApiCreate(BaseModel):
    name: str
    description: str


class KeyApiInDB(KeyApi, KeyApiCreate):
    login: str


class KeyApiInResponse(RWModel):
    key: KeyApiInDB







