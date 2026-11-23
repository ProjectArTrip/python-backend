from dataclasses import dataclass
from typing import Final
from urllib.parse import urlencode

import httpx

from arttrip.application.domain.auth.exceptions import AuthError
from arttrip.application.domain.auth.social_provider import SocialProvider
from arttrip.application.port.output.web_oauth_port import WebOAuthPort

GOOGLE_AUTHORIZATION_ENDPOINT: Final = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT: Final = "https://oauth2.googleapis.com/token"


@dataclass(frozen=True)
class WebProviderConfig:
    authorization_endpoint: str
    token_endpoint: str
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: str


class WebOAuthAdapter(WebOAuthPort):
    def __init__(
        self,
        *,
        http_client: httpx.Client,
        configs: dict[SocialProvider, WebProviderConfig],
    ) -> None:
        self._http_client = http_client
        self._configs = configs

    def build_authorization_url(
        self, *, provider: SocialProvider, state: str, nonce: str
    ) -> str:
        config = self._config_of(provider)
        query = urlencode(
            {
                "client_id": config.client_id,
                "response_type": "code",
                "scope": config.scope,
                "redirect_uri": config.redirect_uri,
                "state": state,
                "nonce": nonce,
            }
        )
        return f"{config.authorization_endpoint}?{query}"

    def exchange_code(self, *, provider: SocialProvider, code: str) -> str:
        config = self._config_of(provider)
        try:
            response = self._http_client.post(
                config.token_endpoint,
                data={
                    "code": code,
                    "client_id": config.client_id,
                    "client_secret": config.client_secret,
                    "redirect_uri": config.redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
        except httpx.TransportError as error:
            raise AuthError.provider_unavailable() from error
        if response.status_code >= 500:
            raise AuthError.provider_unavailable()
        if response.status_code != 200:
            raise AuthError.invalid_id_token()
        try:
            id_token = response.json().get("id_token")
        except ValueError as error:
            raise AuthError.invalid_id_token() from error
        if not isinstance(id_token, str):
            raise AuthError.invalid_id_token()
        return id_token

    def _config_of(self, provider: SocialProvider) -> WebProviderConfig:
        config = self._configs.get(provider)
        if config is None:
            raise AuthError.unsupported_web_provider()
        return config
