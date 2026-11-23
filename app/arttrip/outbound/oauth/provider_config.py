from dataclasses import dataclass
from typing import Final

from arttrip.application.domain.auth.social_provider import SocialProvider


@dataclass(frozen=True)
class ProviderConfig:
    issuers: tuple[str, ...]
    jwks_uri: str
    algorithms: tuple[str, ...]


PROVIDER_CONFIGS: Final[dict[SocialProvider, ProviderConfig]] = {
    SocialProvider.APPLE: ProviderConfig(
        issuers=("https://appleid.apple.com",),
        jwks_uri="https://appleid.apple.com/auth/keys",
        algorithms=("RS256",),
    ),
    SocialProvider.GOOGLE: ProviderConfig(
        issuers=("https://accounts.google.com", "accounts.google.com"),
        jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
        algorithms=("RS256",),
    ),
    SocialProvider.KAKAO: ProviderConfig(
        issuers=("https://kauth.kakao.com",),
        jwks_uri="https://kauth.kakao.com/.well-known/jwks.json",
        algorithms=("RS256",),
    ),
}
