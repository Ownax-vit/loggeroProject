from typing import Optional

from pydantic import EmailStr

from ..core.security import generate_salt
from ..core.security import get_password_hash
from ..core.security import verify_password
from .base import RWModel


# class DBModelMixin(BaseModel):
#     id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")


class UserBase(RWModel):
    login: str
    email: EmailStr


class UserInDB(UserBase):
    salt: str = ""
    hashed_password: str = ""

    def check_password(self, password: str):
        return verify_password(self.salt + password, self.hashed_password)

    def change_password(self, password: str):
        self.salt = generate_salt()
        self.hashed_password = get_password_hash(self.salt + password)


class User(UserBase):
    token: str


class UserInResponse(User):
    pass


class UserInLogin(RWModel):
    email: EmailStr
    password: str


class UserInCreate(UserInLogin):
    login: str


class UserInUpdate(RWModel):
    login: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
