from passlib.context import CryptContext

from src.settings import project_settings


class Hasher:
    def __init__(self):
        self.pwd_context: CryptContext = CryptContext(
            schemes=[project_settings.PWD_SCHEMA, ],
            deprecated=project_settings.PWD_DEPRECATED,
        )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(hashed_password, plain_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
