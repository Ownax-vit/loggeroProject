from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field

from ..core.security import generate_salt
from ..core.security import get_password_hash
from ..core.security import verify_password
from .base import DBModelMixin


class UserBase(DBModelMixin):
    login: str = Field(...)
    email: EmailStr = Field(...)


class UserInDB(UserBase):
    salt: str = Field(default="")
    hashed_password: str = Field(default="")

    def check_password(self, password: str):
        return verify_password(self.salt + password, self.hashed_password)

    def change_password(self, password: str):
        self.salt = generate_salt()
        self.hashed_password = get_password_hash(self.salt + password)


class User(UserBase):
    token: str = Field(...)


class UserInResponse(User):
    pass


class UserInLogin(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)


class UserInCreate(UserInLogin):
    login: str = Field(...)


class UserInUpdate(BaseModel):
    email: EmailStr = Field(default=None)
    password: str = Field(default=None)
