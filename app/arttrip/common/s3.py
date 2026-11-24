from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class S3Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="AWS_", extra="ignore"
    )

    s3_region: str
    s3_bucket_name: str
    s3_connect_timeout_seconds: float = Field(default=5, gt=0)
    s3_read_timeout_seconds: float = Field(default=30, gt=0)
    s3_max_attempts: int = Field(default=3, ge=1, le=10)
    s3_key_prefix: str = ""
    s3_url_expires_seconds: int = Field(default=3600, gt=0, le=604800)
