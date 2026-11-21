from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        extra="ignore",
    )

    host: str = Field(min_length=1)
    port: int = Field(ge=1, le=65535)
    storage_base_url: str = Field(min_length=1)
    storage_timeout_s: float = Field(gt=0)
    log_level: str = Field(min_length=1)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
