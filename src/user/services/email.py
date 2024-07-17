from datetime import datetime
from datetime import timedelta
from typing import List
from uuid import UUID

from fastapi_mail import ConnectionConfig
from fastapi_mail import FastMail
from fastapi_mail import MessageSchema
from jose import jwt
from pydantic import EmailStr

from src.settings import project_settings
from src.user.models import User


class EmailService:
    def __init__(self):
        self.email_conf: ConnectionConfig = ConnectionConfig(
            MAIL_USERNAME=project_settings.MAIL_USERNAME,
            MAIL_PASSWORD=project_settings.MAIL_PASSWORD,
            MAIL_FROM=project_settings.MAIL_FROM,
            MAIL_PORT=project_settings.MAIL_PORT,
            MAIL_SERVER=project_settings.MAIL_SERVER,
            MAIL_STARTTLS=project_settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=project_settings.MAIL_SSL_TLS,
            USE_CREDENTIALS=project_settings.USE_CREDENTIALS,
            VALIDATE_CERTS=project_settings.VALIDATE_CERTS,
        )

    async def send_email(
        self,
        email: List[EmailStr],
        subject: str,
        instance: User,
    ) -> None:
        token: str = self._create_token_for_email_confirmation(
            user_id=instance.user_id,
            email=email,
            instance=instance
        )

        message: MessageSchema = MessageSchema(
            subject=subject,
            recipients=email,
            body=f"Токен для подтверждения регистрации: {token}",
            subtype="html",
        )

        fm: FastMail = FastMail(self.email_conf)

        await fm.send_message(message=message)

    @staticmethod
    def _create_token_for_email_confirmation(
            user_id: UUID,
            email: str,
            instance: User
    ) -> str:
        current_time: datetime = datetime.utcnow()
        expiration_time: datetime = current_time + timedelta(
            seconds=project_settings.MAIL_CONFIRMATION_TOKEN_EXPIRE_SECONDS
        )

        token_data: dict = {
            "user_id": user_id,
            "exp": expiration_time,
        }

        if instance.email != email:
            token_data["email"] = email

        token: str = jwt.encode(
            token_data,
            project_settings.SECRET_KEY,
            algorithm=project_settings.ALGORITHM,
        )

        return token
