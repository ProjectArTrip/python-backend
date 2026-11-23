from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenDataSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="OPENDATA_", extra="ignore"
    )

    service_key: SecretStr
    base_url: str = "https://apis.data.go.kr/B553457/cultureinfo"
    page_size: int = Field(default=20, ge=1, le=100)
    timeout_seconds: float = Field(default=10, gt=0)
    excluded_areas: list[str] = Field(default_factory=lambda: ["인천"])
