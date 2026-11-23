from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="DB_", extra="ignore")

    host: str
    port: int
    user: str
    password: str
    name: str
    pool_size: int = Field(default=5, ge=1)
    pool_max_overflow: int = Field(default=10, ge=0)
    pool_timeout_seconds: int = Field(default=30, ge=1)
    pool_recycle_seconds: int = Field(default=-1, ge=-1)

    @property
    def url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            host=self.host,
            port=self.port,
            username=self.user,
            password=self.password,
            database=self.name,
        )
