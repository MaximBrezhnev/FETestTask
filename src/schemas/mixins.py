import re
from typing import ClassVar, Optional

from pydantic import field_validator, model_validator


class UsernameValidationMixin:
    """
    Миксин, производящий валидацию поступившего на вход username с
    точки зрения допустимых символов и длины
    """

    LETTER_MATCH_PATTERN: ClassVar[re.Pattern] = re.compile(r"^[0-9а-яА-Яa-zA-Z\-_]+$")
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
    """
    Миксин, производящий валидацию поступивших на вход name и surname с
    точки зрения допустимых символов и длины
    """

    NAME_LETTER_MATCH_PATTERN: ClassVar[re.Pattern] = re.compile(r"^[а-яА-Яa-zA-Z\- ]+$")
    MIN_LENGTH: ClassVar[int] = 1
    MAX_LENGTH: ClassVar[int] = 20

    @field_validator("name", check_fields=False)
    @classmethod
    def validate_name(cls, name: Optional[str]) -> Optional[str]:
        if name is not None:
            if (
                    len(name) < cls.MIN_LENGTH
                    or len(name) > cls.MAX_LENGTH
            ):
                raise ValueError("Incorrect name length")

            if not cls.NAME_LETTER_MATCH_PATTERN.match(name):
                raise ValueError("The name contains incorrect symbols")

            return name

    @field_validator("surname", check_fields=False)
    @classmethod
    def validate_surname(cls, surname: Optional[str]) -> Optional[str]:
        if surname is not None:
            if (
                    len(surname) < cls.MIN_LENGTH
                    or len(surname) > cls.MAX_LENGTH
            ):
                raise ValueError("Incorrect surname length")

            if not cls.NAME_LETTER_MATCH_PATTERN.match(surname):
                raise ValueError("The surname contains incorrect symbols")

            return surname


class PasswordValidationMixin:
    """
    Миксин, производящий валидацию пароля. Проверяется
    его сложность и совпадение паролей при подтверждении
    """

    MIN_PASSWORD_LENGTH: ClassVar[int] = 8
    PASSWORD_SPECIAL_SYMBOLS: ClassVar[str] = "!@#$%^&*()-_=+[{]};:'\",<.>/?\\|`~"

    @classmethod
    def check_password_strength(cls, password: str) -> bool:
        """
        Метод, производящий проверку пароля на надежность
        """
        if len(password) < cls.MIN_PASSWORD_LENGTH:
            return False

        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_digit = any(char.isdigit() for char in password)
        has_special = any(char in cls.PASSWORD_SPECIAL_SYMBOLS for char in password)

        return has_upper and has_lower and has_digit and has_special

    @field_validator("password1", check_fields=False)
    @classmethod
    def validate_password(cls, password: str) -> str:
        """
        В случае прохождения проверки на сложность метод возвращает
        пароль. В обратном случае возникает исключение
        """

        if not cls.check_password_strength(password=password):
            raise ValueError("The password is weak")

        return password

    @model_validator(mode="before")
    @classmethod
    def check_password_match(cls, data: dict) -> dict:
        """
        В случае совпадения паролей метод возвращает
        данные, поступившие на валидацию
        В обратном случае возникает исключение
        """

        if data.get("password1") != data.get("password2"):
            raise ValueError("The passwords do not match")

        return data
