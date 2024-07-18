from typing import Optional

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.services.security import get_email_from_jwt_token

from src.database.config import database_settings
from src.database.models import User
from src.services.service import UserService


async def get_db_session() -> AsyncSession:
    """
    Зависимость, возвращающая асинхронную сессию для работы с базой данных
    и закрывающая ее после окончания ее использования
    """

    try:
        session: AsyncSession = database_settings.async_session()
        yield session
    finally:
        await session.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db_session: AsyncSession = Depends(get_db_session),
) -> User:
    """
    Зависимость, возвращающая текущего пользователя,
    используя данные из заголовков

    В случае ошибок, связанных с токеном доступа или данным пользователя
    возвращает исключение с кодом 401

    В случае корректной работы возвращает текущего пользователя
    """

    try:
        email: Optional[str] = get_email_from_jwt_token(token=token)
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user: Optional[User] = await _get_user_by_email_from_database(
        email=email, db_session=db_session
    )
    if user is None:
        raise credentials_exception
    if not user.is_verified:
        raise credentials_exception

    return user


async def _get_user_by_email_from_database(
        email: str,
        db_session: AsyncSession
) -> Optional[User]:
    """
    Вспомогательная функция, используемая зависимостью
    get_current_user для получения пользователя из базы данных по его e-mail
    """

    async with db_session:
        query = select(User).filter_by(email=email)
        result = await db_session.execute(query)
    return result.scalars().first()


def get_user_service(
        db_session: AsyncSession = Depends(get_db_session)
) -> UserService:
    """
    Зависимость, возвращающая объект класса UserService c сессией,
    полученной из зависимости get_db_session
    """

    return UserService(db_session=db_session)
