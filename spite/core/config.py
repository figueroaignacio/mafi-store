from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    groq_api_key: str
    database_url: str = "sqlite+aiosqlite:///./spite.db"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    log_level: str = "INFO"
    browser: str = "firefox"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
