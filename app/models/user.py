from typing import Optional


from pydantic import EmailStr, BaseModel
from ..core.security import generate_salt, get_password_hash, verify_password
from .rwmodel import RWModel


class DBModelMixin(BaseModel):
    id: Optional[int] = None


class UserBase(RWModel):
    login: str
    email: EmailStr


class UserInDB(DBModelMixin, UserBase):
    salt: str = ""
    hashed_password: str = ""

    def check_password(self, password: str):
        return verify_password(self.salt + password, self.hashed_password)

    def change_password(self, password: str):
        self.salt = generate_salt()
        self.hashed_password = get_password_hash(self.salt + password)


class User(UserBase):
    token: str


class UserInResponse(RWModel):
    user: User


class UserInLogin(RWModel):
    email: EmailStr
    password: str


class UserInCreate(UserInLogin):
    login: str

class UserInUpdate(RWModel):
    login: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
