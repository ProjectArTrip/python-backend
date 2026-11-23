from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ExhibitSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="EXHIBIT_", extra="ignore"
    )

    ending_soon_days: int = Field(default=3, ge=0)
    recent_list_size: int = Field(default=20, ge=1, le=50)
    recent_retention_days: int = Field(default=14, ge=1)
    import_max_bytes: int = Field(default=5 * 1024 * 1024, ge=1)
    import_max_uncompressed_bytes: int = Field(default=50 * 1024 * 1024, ge=1)
    import_max_rows: int = Field(default=1000, ge=1)
