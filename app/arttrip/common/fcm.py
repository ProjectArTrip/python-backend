from pydantic_settings import BaseSettings, SettingsConfigDict


class PushSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    firebase_credentials_path: str
    timeout_seconds: int = 10
