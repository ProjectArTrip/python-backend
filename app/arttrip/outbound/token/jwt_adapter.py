import secrets
from datetime import UTC, datetime, timedelta
from typing import Final

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from arttrip.application.domain.auth.exceptions import AuthError
from arttrip.application.domain.user.role import UserRole
from arttrip.application.port.output.token_port import AccessTokenClaims, TokenPort

ALGORITHM: Final = "HS256"
ACCESS_TOKEN_TYPE: Final = "access"


class JwtTokenAdapter(TokenPort):
    def __init__(
        self,
        *,
        issuer: str,
        secret: str,
        access_expiration_seconds: int,
    ) -> None:
        self._issuer = issuer
        self._secret = secret
        self._access_expiration = timedelta(seconds=access_expiration_seconds)

    def issue_access_token(self, *, user_id: int, role: UserRole, now: datetime) -> str:
        payload = {
            "iss": self._issuer,
            "sub": str(user_id),
            "role": role.value,
            "iat": now,
            "exp": now + self._access_expiration,
            "jti": secrets.token_urlsafe(16),
            "typ": ACCESS_TOKEN_TYPE,
        }
        return jwt.encode(payload, self._secret, algorithm=ALGORITHM)

    def verify_access_token(self, token: str) -> AccessTokenClaims:
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=[ALGORITHM],
                issuer=self._issuer,
                options={"require": ["iss", "sub", "exp", "iat", "jti"]},
            )
        except ExpiredSignatureError as error:
            raise AuthError.expired_access_token() from error
        except InvalidTokenError as error:
            raise AuthError.invalid_access_token() from error

        if payload.get("typ") != ACCESS_TOKEN_TYPE:
            raise AuthError.invalid_access_token()

        try:
            return AccessTokenClaims(
                user_id=int(payload["sub"]),
                role=UserRole(payload["role"]),
                token_id=str(payload["jti"]),
                expires_at=datetime.fromtimestamp(payload["exp"], tz=UTC),
            )
        except (KeyError, ValueError) as error:
            raise AuthError.invalid_access_token() from error
