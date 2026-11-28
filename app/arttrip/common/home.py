from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class HomeSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="HOME_", extra="ignore"
    )

    today_size: int = Field(default=3, ge=1, le=20)
    genre_size: int = Field(default=3, ge=1, le=20)
    venue_size: int = Field(default=3, ge=1, le=20)
    curation_size: int = Field(default=3, ge=1, le=20)
