from functools import lru_cache
from typing import Annotated

from pydantic import AfterValidator
from pydantic_settings import BaseSettings, SettingsConfigDict


def log_level_after(log_level: str) -> str:
    return log_level.upper()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    log_level: Annotated[str, AfterValidator(log_level_after)] = "INFO"

    # OpenAI Configuration
    # openai_api_key: str

    # CORS Configuration
    cors_allowed_origins: str = "http://localhost:3000"

    # A2A Configuration
    a2a_base_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
