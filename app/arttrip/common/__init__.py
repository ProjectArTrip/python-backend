from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from arttrip.common.database import DatabaseSettings
from arttrip.common.exhibit import ExhibitSettings
from arttrip.common.fcm import PushSettings
from arttrip.common.home import HomeSettings
from arttrip.common.http import HttpSettings
from arttrip.common.image import ImageSettings
from arttrip.common.jwt import JwtSettings
from arttrip.common.keyword import KeywordSettings
from arttrip.common.log import LogSettings
from arttrip.common.oauth import OAuthSettings
from arttrip.common.opendata import OpenDataSettings
from arttrip.common.redis import RedisSettings
from arttrip.common.s3 import S3Settings
from arttrip.common.search_history import SearchHistorySettings
from arttrip.common.web_auth import WebAuthSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    oauth: OAuthSettings = Field(default_factory=OAuthSettings)
    http: HttpSettings = Field(default_factory=HttpSettings)
    jwt: JwtSettings = Field(default_factory=JwtSettings)
    exhibit: ExhibitSettings = Field(default_factory=ExhibitSettings)
    home_screen: HomeSettings = Field(default_factory=HomeSettings)
    web_auth: WebAuthSettings = Field(default_factory=WebAuthSettings)
    s3: S3Settings = Field(default_factory=S3Settings)
    image: ImageSettings = Field(default_factory=ImageSettings)
    log: LogSettings = Field(default_factory=LogSettings)
    search_history: SearchHistorySettings = Field(default_factory=SearchHistorySettings)
    keyword: KeywordSettings = Field(default_factory=KeywordSettings)
    push: PushSettings = Field(default_factory=PushSettings)
    opendata: OpenDataSettings = Field(default_factory=OpenDataSettings)


settings = Settings()
