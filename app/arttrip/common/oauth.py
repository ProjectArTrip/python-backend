from typing import Annotated, Any

from pydantic import BeforeValidator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


def split_comma(value: Any) -> Any:
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return value


CommaSeparated = Annotated[list[str], NoDecode, BeforeValidator(split_comma)]


class OAuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="OAUTH_", extra="ignore"
    )
    apple_audiences: CommaSeparated
    kakao_audiences: CommaSeparated
    timeout_seconds: float = 3.0
    leeway_seconds: int = 30
