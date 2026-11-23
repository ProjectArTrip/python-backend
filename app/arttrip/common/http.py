from pydantic_settings import BaseSettings, SettingsConfigDict


class HttpSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="HTTP_", extra="ignore"
    )

    docs_enabled: bool = False
