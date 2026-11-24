from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class HttpSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="HTTP_", extra="ignore"
    )

    docs_enabled: bool = False
    max_body_bytes: int = Field(default=10 * 1024 * 1024, ge=1)
