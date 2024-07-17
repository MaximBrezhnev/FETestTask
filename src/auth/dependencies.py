from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from src.auth.services import get_email_from_jwt_token
from src.dependencies import get_db_session
from src.user.models import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db_session: AsyncSession = Depends(get_db_session),
) -> User:
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
    async with db_session:
        query = select(User).filter_by(email=email)
        result = await db_session.execute(query)
    return result.scalars().first()