from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    """
    Модель для представления пользователей в базе данных.

    Атрибуты:
    user_id (UUID): Уникальный идентификатор пользователя, генерируется автоматически.
    name (str): Имя пользователя.
    surname (str): Фамилия пользователя.
    username (str): Уникальное имя пользователя (логин).
    email (str): Уникальный email пользователя.
    hashed_password (str): Захешированный пароль пользователя.
    created_at (datetime): Дата и время создания записи, по умолчанию устанавливается текущее время в UTC.
    updated_at (datetime): Дата и время последнего обновления записи, по умолчанию устанавливается текущее время в UTC и
     обновляется автоматически при изменении записи.
    is_verified (bool): Статус верификации пользователя, по умолчанию False, после подтверждения адреса электронной
     почты устанавливается в True.
    """

    __tablename__ = "user"

    user_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]
    surname: Mapped[str]
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE ('utc', now())")
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE ('utc', now())"),
        onupdate=datetime.utcnow,
    )
    is_verified: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"User:{self.email}"
