from dataclasses import dataclass
from datetime import datetime

from arttrip.application.domain.user.onboarding_step import OnboardingStep
from arttrip.application.domain.user.role import UserRole


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: int
    role: UserRole
    token_id: str
    token_expires_at: datetime


@dataclass(frozen=True)
class SignInResult:
    tokens: TokenPair
    onboarding_step: OnboardingStep


@dataclass(frozen=True)
class WebSignInStart:
    authorization_url: str
    state: str
    nonce: str
