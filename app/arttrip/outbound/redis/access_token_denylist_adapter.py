from datetime import datetime
from typing import Final

from redis import Redis

from arttrip.application.port.output.access_token_denylist_port import (
    AccessTokenDenylistPort,
)

KEY_PREFIX: Final = "auth:denied:"


class RedisAccessTokenDenylistAdapter(AccessTokenDenylistPort):
    def __init__(self, *, client: Redis) -> None:
        self._client = client

    def deny(self, *, token_id: str, expires_at: datetime) -> None:
        self._client.set(self._key(token_id), "1", exat=int(expires_at.timestamp()))

    def is_denied(self, token_id: str) -> bool:
        return self._client.exists(self._key(token_id)) > 0

    @staticmethod
    def _key(token_id: str) -> str:
        return f"{KEY_PREFIX}{token_id}"
