import hashlib
import secrets
from typing import Final

from redis import Redis

from arttrip.application.port.output.refresh_token_port import RefreshTokenPort

KEY_PREFIX: Final = "auth:refresh:"
TOKEN_BYTES: Final = 32


class RedisRefreshTokenAdapter(RefreshTokenPort):
    def __init__(self, *, client: Redis, expiration_seconds: int) -> None:
        self._client = client
        self._expiration_seconds = expiration_seconds

    def issue(self, *, user_id: int) -> str:
        token = secrets.token_urlsafe(TOKEN_BYTES)
        self._client.set(self._key(token), str(user_id), ex=self._expiration_seconds)
        return token

    def consume(self, token: str) -> int | None:
        value = self._client.getdel(self._key(token))
        if value is None:
            return None
        return int(value)

    @staticmethod
    def _key(token: str) -> str:
        digest = hashlib.sha256(token.encode()).hexdigest()
        return f"{KEY_PREFIX}{digest}"
