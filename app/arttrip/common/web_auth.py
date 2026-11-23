from typing import Literal, Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from arttrip.common.oauth import CommaSeparated


class WebAuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    google_client_id: str
    google_client_secret: SecretStr
    google_redirect_uri: str
    success_redirect_url: str
    failure_redirect_url: str
    cookie_secure: bool
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    state_max_age_seconds: int = Field(default=600, gt=0)
    allowed_origins: CommaSeparated

    @model_validator(mode="after")
    def _none_requires_secure(self) -> Self:
        if self.cookie_samesite == "none" and not self.cookie_secure:
            raise ValueError(
                "WEB_AUTH_COOKIE_SAMESITE=none requires COOKIE_SECURE=true"
            )
        return self
