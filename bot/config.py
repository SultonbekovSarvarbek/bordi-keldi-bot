from __future__ import annotations

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурация приложения, читается из переменных окружения / .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Telegram
    bot_token: str
    # Список ID админов задаётся как "111,222" — храним строкой, парсим в .admin_ids
    admin_ids_raw: str = Field("", validation_alias="ADMIN_IDS")
    group_id: int | None = None

    # PostgreSQL
    postgres_user: str = "bordi"
    postgres_password: str = "bordi"
    postgres_db: str = "bordi"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # Бизнес-параметры
    search_date_window: int = 2
    search_limit: int = 20
    tz: str = "Asia/Tashkent"
    deactivate_hour: int = 3

    @property
    def admin_ids(self) -> list[int]:
        # Позволяем задавать ADMIN_IDS как "111,222" в .env
        return [int(x) for x in self.admin_ids_raw.replace(" ", "").split(",") if x]

    @field_validator("group_id", mode="before")
    @classmethod
    def _empty_group_to_none(cls, v: object) -> object:
        if v in ("", None):
            return None
        return v

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()
