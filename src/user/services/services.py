from datetime import timedelta
from typing import Optional, List, Dict

from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt
from jose import JWTError

from src.auth.services import create_jwt_token
from src.settings import project_settings
from src.user.models import User
from src.user.services.dal import UserDAL
from src.user.services.email import EmailService
from src.user.services.hashing import Hasher


class UserService:
    def __init__(self, db_session: AsyncSession):
        self.dal: UserDAL = UserDAL(db_session=db_session)
        self.hasher: Hasher = Hasher()
        self.email = EmailService()

    async def create_user(
            self,
            name: str,
            surname: str,
            email: str,
            username: str,
            password: str
    ) -> None:
        user: User = await self.dal.create_new_user(
            name=name,
            surname=surname,
            username=username,
            email=email,
            hashed_password=self.hasher.get_password_hash(password=password),
        )

        await self.email.send_email(
            email=[
                user.email,
            ],
            instance=user,
            subject="Письмо для подтверждения регистрации",
        )

    async def verify_email(self, token: str) -> User:
        payload: dict = jwt.decode(
            token, project_settings.SECRET_KEY,
            algorithms=["HS256"]
        )

        user: Optional[User] = await self.dal.get_user_by_id(
            user_id=payload.get("user_id", None)
        )
        if user is None:
            raise JWTError("Could not validate credentials")

        user: User = await self.dal.verify_user(user=user)
        return user

    async def get_users(self) -> List[User]:
        users: List[User] = await self.dal.get_users()
        return users

    async def delete_user(self, user: User) -> None:
        await self.dal.delete_user(user=user)

    async def login(self, username: str, password: str) -> dict:
        user: Optional[User] = await self.dal.get_user_by_username(username=username)

        if user is None:
            raise ValueError("User does not exist")

        if not user.is_verified:
            raise ValueError("User is not verified")

        if not self.hasher.verify_password(
                hashed_password=user.hashed_password,
                plain_password=password
        ):
            raise ValueError("Passwords do not match")

        access_token: str = create_jwt_token(
            user.email, timedelta(minutes=project_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token: str = create_jwt_token(
            user.email, timedelta(days=project_settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    def refresh_token(user: User) -> dict:
        new_access_token: str = create_jwt_token(
            email=user.email,
            exp_timedelta=timedelta(
                minutes=project_settings.ACCESS_TOKEN_EXPIRE_MINUTES
            ),
        )
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    async def update_user(
            self,
            user: User,
            parameters_for_update: Dict[str: str],
    ) -> User:
        updated_user: User = await self.dal.update_user(
            user=user,
            parameters_for_update=parameters_for_update
        )
        return updated_user

    async def change_password(
            self,
            user: User,
            old_password: str,
            new_password: str,
    ) -> User:
        if not self.hasher.verify_password(
                hashed_password=user.hashed_password,
                plain_password=old_password
        ):
            raise ValueError("Incorrect old password")

        updated_user: Optional[User] = await self.dal.change_password(
            user=user,
            new_password=self.hasher.get_password_hash(new_password),
        )

        return updated_user

    async def change_email(self, user: User, new_email: str) -> None:
        if user.email == new_email:
            raise ValueError("The user already uses this email")

        await self.email.send_email(
            email=[new_email, ],
            instance=user,
            subject="Письмо для подтверждения смены электронной почты",
        )

    async def confirm_email_change(self, token: str) -> User:
        payload: dict = jwt.decode(
            token,
            project_settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        user: Optional[User] = await self.dal.get_user_by_id(
            user_id=payload.get("user_id", None)
        )

        if user is None:
            raise JWTError("Could not validate credentials")

        if not user.is_verified:
            raise ValueError("User is not verified")

        new_email: str = payload.get("email", None)
        if new_email is None:
            raise JWTError("Could not validate credentials")

        updated_user: User = await self.dal.change_email(
            user=user,
            new_email=new_email,
        )

        return updated_user
