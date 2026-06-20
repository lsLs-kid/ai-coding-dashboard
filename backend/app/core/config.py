from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Coding Operations Dashboard"
    api_prefix: str = "/api"
    data_provider: str = "mock"
    database_url: str = "postgresql+asyncpg://aicoding:aicoding@localhost:5432/aicoding"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_prefix="AICODING_")


@lru_cache
def get_settings() -> Settings:
    return Settings()
