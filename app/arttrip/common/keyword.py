from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class KeywordSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="KEYWORD_", extra="ignore"
    )

    recommended_size: int = Field(default=5, ge=1, le=20)
