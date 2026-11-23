from abc import ABC, abstractmethod

from arttrip.application.domain.auth.social_provider import SocialProvider


class WebOAuthPort(ABC):
    @abstractmethod
    def build_authorization_url(
        self, *, provider: SocialProvider, state: str, nonce: str
    ) -> str:
        pass

    @abstractmethod
    def exchange_code(self, *, provider: SocialProvider, code: str) -> str:
        pass
