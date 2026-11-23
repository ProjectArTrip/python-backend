from abc import ABC, abstractmethod

from arttrip.application.domain.auth.social_provider import SocialProvider
from arttrip.application.port.input.auth.commands import (
    CompleteWebSignInCommand,
    ReissueTokensCommand,
    SignInCommand,
    SignOutCommand,
    SignOutWebCommand,
)
from arttrip.application.port.input.auth.results import (
    AuthenticatedUser,
    SignInResult,
    TokenPair,
    WebSignInStart,
)


class AuthenticateUseCase(ABC):
    @abstractmethod
    def authenticate(self, access_token: str | None) -> AuthenticatedUser:
        pass


class SignInUseCase(ABC):
    @abstractmethod
    def sign_in(self, command: SignInCommand) -> SignInResult:
        pass


class ReissueTokensUseCase(ABC):
    @abstractmethod
    def reissue_tokens(self, command: ReissueTokensCommand) -> TokenPair:
        pass


class SignOutUseCase(ABC):
    @abstractmethod
    def sign_out(self, command: SignOutCommand) -> None:
        pass


class StartWebSignInUseCase(ABC):
    @abstractmethod
    def start_web_sign_in(self, provider: SocialProvider) -> WebSignInStart:
        pass


class CompleteWebSignInUseCase(ABC):
    @abstractmethod
    def complete_web_sign_in(self, command: CompleteWebSignInCommand) -> TokenPair:
        pass


class SignOutWebUseCase(ABC):
    @abstractmethod
    def sign_out_web(self, command: SignOutWebCommand) -> None:
        pass
