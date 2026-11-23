from abc import ABC, abstractmethod
from dataclasses import dataclass

from arttrip.application.domain.auth.social_provider import SocialProvider


@dataclass(frozen=True)
class VerifiedIdentity:
    provider: SocialProvider
    subject: str
    email: str | None
    nonce: str | None = None


class OAuthPort(ABC):
    @abstractmethod
    def verify(self, *, provider: SocialProvider, id_token: str) -> VerifiedIdentity:
        pass
