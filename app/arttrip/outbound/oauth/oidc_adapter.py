import logging

import jwt
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError, PyJWKClientError

from arttrip.application.domain.auth.exceptions import AuthError
from arttrip.application.domain.auth.social_provider import SocialProvider
from arttrip.application.port.output.oauth_port import OAuthPort, VerifiedIdentity
from arttrip.outbound.oauth.provider_config import PROVIDER_CONFIGS

_logger = logging.getLogger(__name__)


class OidcOAuthAdapter(OAuthPort):
    def __init__(
        self,
        *,
        jwk_clients: dict[SocialProvider, PyJWKClient],
        audiences: dict[SocialProvider, list[str]],
        leeway_seconds: int,
    ) -> None:
        self._jwk_clients = jwk_clients
        self._audiences = audiences
        self._leeway_seconds = leeway_seconds

    def verify(self, *, provider: SocialProvider, id_token: str) -> VerifiedIdentity:
        config = PROVIDER_CONFIGS[provider]

        try:
            signing_key = self._jwk_clients[provider].get_signing_key_from_jwt(id_token)
        except PyJWKClientError as error:
            raise AuthError.provider_unavailable() from error
        except InvalidTokenError as error:
            _logger.warning(
                "id token rejected: provider=%s reason=%s",
                provider.value,
                type(error).__name__,
            )
            raise AuthError.invalid_id_token() from error

        try:
            payload = jwt.decode(
                id_token,
                signing_key,
                algorithms=list(config.algorithms),
                audience=self._audiences[provider],
                issuer=config.issuers,
                leeway=self._leeway_seconds,
                options={"require": ["iss", "aud", "sub", "exp", "iat"]},
            )
        except InvalidTokenError as error:
            _logger.warning(
                "id token rejected: provider=%s reason=%s",
                provider.value,
                type(error).__name__,
            )
            raise AuthError.invalid_id_token() from error

        return VerifiedIdentity(
            provider=provider,
            subject=payload["sub"],
            email=payload.get("email"),
            nonce=payload.get("nonce"),
        )
