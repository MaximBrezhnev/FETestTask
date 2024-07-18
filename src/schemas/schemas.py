from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict

from src.schemas.mixins import UsernameValidationMixin, NameAndSurnameValidationMixin, PasswordValidationMixin


class UserCreationSchema(
    NameAndSurnameValidationMixin,
    UsernameValidationMixin,
    PasswordValidationMixin,
    BaseModel
):
    """
    Схема для валидации данных при создании пользователя.

    Атрибуты:
    name (str): Имя пользователя;
    surname (str): Фамилия пользователя;
    username (str): Уникальное имя пользователя (логин);
    email (EmailStr): Электронная почта пользователя;
    password1 (str): Пароль пользователя;
    password2 (str): Повторение пароля для подтверждения;
    """

    name: str
    surname: str
    username: str
    email: EmailStr
    password1: str
    password2: str


class ShowUserSchema(BaseModel):
    """
    Схема для отображения информации о пользователе.

    Атрибуты:
    name (str): Имя пользователя.
    surname (str): Фамилия пользователя.
    username (str): Уникальное имя пользователя (логин).
    email (EmailStr): Электронная почта пользователя.
    """
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
    """
    Схема для обновления информации о пользователе, смена которой не требует
    дополнительного подтверждения

    Атрибуты:
    name (Optional[str]): Новое имя пользователя (необязательно);
    surname (Optional[str]): Новая фамилия пользователя (необязательно);
    username (Optional[str]): Новое уникальное имя пользователя (необязательно).
    """

    name: Optional[str] = None
    surname: Optional[str] = None
    username: Optional[str] = None


class EmailSchema(BaseModel):
    """
    Схема для валидации данных при смене адреса электронной почты

    Атрибуты:
    email (str): Адрес новой электронной почты
    """

    email: EmailStr


class ChangePasswordSchema(
    PasswordValidationMixin,
    BaseModel
):
    """
    Схема для изменения пароля пользователя.

    Атрибуты:
    old_password (str): Текущий пароль пользователя.
    password1 (str): Новый пароль пользователя.
    password2 (str): Подтверждение нового пароля.
    """

    old_password: str
    password1: str
    password2: str


class TokenSchema(BaseModel):
    """
    Схема для представления access token'а и refresh token'а.

    Атрибуты:
    access_token (str): Токен доступа.
    refresh_token (Optional[str]): Refresh token. Если с помощью схемы происходит обновление токена доступа, то
    refresh token не возвращается, следовательно, поле остается пустым.
    token_type (str): Тип токена, обычно "Bearer".
    """

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str
