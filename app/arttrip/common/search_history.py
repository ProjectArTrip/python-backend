from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SearchHistorySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="SEARCH_HISTORY_", extra="ignore"
    )

    max_count: int = Field(default=10, ge=1, le=50)
    max_length: int = Field(default=50, ge=1, le=255)
