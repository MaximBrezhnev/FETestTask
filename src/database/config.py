import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


class DatabaseSettings(BaseSettings):
    """
    Класс, представляющий собой настройки соединения с базой данных
    """

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def ASYNC_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def _async_engine(self):
        return create_async_engine(url=self.ASYNC_DATABASE_URL, future=True, echo=True)

    @property
    def async_session(self):
        return async_sessionmaker(self._async_engine, expire_on_commit=False)

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))
                )
            ),
            ".env"
        ),
        extra="ignore",
    )


database_settings = DatabaseSettings()
