from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ImageSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="IMAGE_", extra="ignore"
    )

    max_bytes: int = Field(default=2 * 1024 * 1024, ge=1)
    max_pixels: int = Field(default=50_000_000, ge=1)
    default_profile_key: str = Field(min_length=1)
    jpeg_quality: int = Field(default=85, ge=1, le=95)
