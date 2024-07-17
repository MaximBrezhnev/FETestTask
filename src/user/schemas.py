from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict

from src.schema_mixins import UsernameValidationMixin
from src.schema_mixins import NameAndSurnameValidationMixin
from src.schema_mixins import PasswordValidationMixin


class UserCreationSchema(
    UsernameValidationMixin,
    NameAndSurnameValidationMixin,
    PasswordValidationMixin,
    BaseModel
):
    name: str
    surname: str
    username: str
    email: EmailStr
    password1: str
    password2: str


class ShowUserSchema(BaseModel):
    name: str
    surname: str
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UpdateUserSchema(
    NameAndSurnameValidationMixin,
    UsernameValidationMixin,
    BaseModel
):
    name: Optional[str] = None
    surname: Optional[str] = None
    username: Optional[str] = None


class EmailSchema(BaseModel):
    email: EmailStr


class ChangePasswordSchema(
    PasswordValidationMixin,
    BaseModel
):
    old_password: str
    password1: str
    password2: str

