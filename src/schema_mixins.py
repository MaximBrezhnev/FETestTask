import re
from typing import ClassVar, Optional

from pydantic import field_validator
from pydantic import model_validator


class UsernameValidationMixin:
    LETTER_MATCH_PATTERN: ClassVar[re.Pattern] = re.compile(r"^[0-9а-яА-Яa-zA-Z\-_ ]+$")
    MIN_USERNAME_LENGTH: ClassVar[int] = 1
    MAX_USERNAME_LENGTH: ClassVar[int] = 20

    @field_validator("username", check_fields=False)
    @classmethod
    def validate_username(cls, username: Optional[str]) -> Optional[str]:
        if username is not None:
            if (
                len(username) < cls.MIN_USERNAME_LENGTH
                or len(username) > cls.MAX_USERNAME_LENGTH
            ):
                raise ValueError("Incorrect username length")

            if not cls.LETTER_MATCH_PATTERN.match(username):
                raise ValueError("The username contains incorrect symbols")

            return username


class NameAndSurnameValidationMixin:
    LETTER_MATCH_PATTERN: ClassVar[re.Pattern] = re.compile(r"^[а-яА-Яa-zA-Z\-]")
    MIN_LENGTH: ClassVar[int] = 1
    MAX_LENGTH: ClassVar[int] = 20

    @field_validator("name", check_fields=False)
    @classmethod
    def validate_username(cls, name: Optional[str]) -> Optional[str]:
        if name is not None:
            if (
                    len(name) < cls.MIN_LENGTH
                    or len(name) > cls.MIN_LENGTH
            ):
                raise ValueError("Incorrect name length")

            if not cls.LETTER_MATCH_PATTERN.match(name):
                raise ValueError("The name contains incorrect symbols")

            return name

    @field_validator("surname", check_fields=False)
    @classmethod
    def validate_username(cls, surname: Optional[str]) -> Optional[str]:
        if surname is not None:
            if (
                    len(surname) < cls.MIN_LENGTH
                    or len(surname) > cls.MIN_LENGTH
            ):
                raise ValueError("Incorrect surname length")

            if not cls.LETTER_MATCH_PATTERN.match(surname):
                raise ValueError("The surname contains incorrect symbols")

            return surname


class PasswordValidationMixin:
    MIN_PASSWORD_LENGTH: ClassVar[int] = 4

    @field_validator("password1", check_fields=False)
    @classmethod
    def validate_password(cls, password: str) -> str:
        if len(password) < cls.MIN_PASSWORD_LENGTH:
            raise ValueError("The password is weak")

        return password

    @model_validator(mode="before")
    @classmethod
    def check_password_match(cls, data: dict) -> dict:
        if data.get("password1") != data.get("password2"):
            raise ValueError("The passwords do not match")

        return data
