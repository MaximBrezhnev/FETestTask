from passlib.context import CryptContext

from src.settings import project_settings


class Hasher:
    """
    Класс для работы с хешированием паролей
    """

    def __init__(self):
        """Инициализация объекта класса путем конфигурации метода хеширования"""

        self.pwd_context: CryptContext = CryptContext(
            schemes=[project_settings.PWD_SCHEMA, ],
            deprecated=project_settings.PWD_DEPRECATED,
        )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Метод, проверяющий, совпадает ли 'сырой' пароль с уже хэшированным"""

        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
