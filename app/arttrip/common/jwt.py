from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class JwtSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="JWT_", extra="ignore"
    )
    issuer: str
    secret: SecretStr = Field(min_length=32)
    access_expiration: int = Field(gt=0)
    refresh_expiration: int = Field(gt=0)
