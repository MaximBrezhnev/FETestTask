from typing import List, Optional, Dict
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.models import User


class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session: AsyncSession = db_session

    async def get_user_by_id(self, user_id: UUID) -> User:
        async with self.db_session.begin():
            query = select(User).filter_by(user_id=user_id)
            result = await self.db_session.execute(query)
        return result.scalars().first()

    async def create_new_user(
            self,
            name: str,
            surname: str,
            username: str,
            email: str,
            hashed_password: str
    ) -> User:
        async with self.db_session.begin():
            new_user: User = User(
                name=name,
                surname=surname,
                username=username,
                email=email,
                hashed_password=hashed_password
            )
            self.db_session.add(new_user)
            await self.db_session.flush()

        return new_user

    async def verify_user(self, user: User) -> None:
        if not user.is_verified:
            async with self.db_session.begin():
                setattr(user, "is_verified", True)

    async def get_users(self) -> List[User]:
        async with self.db_session.begin():
            query = select(User)
            result = await self.db_session.execute(query)

        return result.scalars().all()

    async def delete_user(self, user: User) -> None:
        async with self.db_session.begin():
            await self.db_session.delete(user)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        async with self.db_session.begin():
            query = select(User).filter_by(username=username)
            result = await self.db_session.execute(query)

        return result.scalars().first()

    async def update_user(
            self,
            user: User,
            parameters_for_update: Dict[str: str]
    ) -> User:
        async with self.db_session.begin():
            if name := parameters_for_update.get("name", None) is not None:
                setattr(user, "name", name)
            if surname := parameters_for_update("surname", None) is not None:
                setattr(user, "surname", surname)
            if username := parameters_for_update("username, None") is not None:
                setattr(user, "username", username)

        return user

    async def change_password(self, user: User, new_password: str) -> User:
        async with self.db_session.begin():
            query = (
                update(User).
                filter_by(user_id=user.user_id).
                values(hashed_password=new_password).
                returning(User)
            )

            result = await self.db_session.execute(query)

        return result.scalars().first()

    async def change_email(self, user: User, new_email: str) -> User:
        async with self.db_session.begin():
            setattr(user, "email", new_email)

        return user


