from dataclasses import dataclass
from datetime import datetime

from arttrip.application.domain.auth.social_provider import SocialProvider


@dataclass(frozen=True)
class SignInCommand:
    provider: SocialProvider
    id_token: str


@dataclass(frozen=True)
class ReissueTokensCommand:
    refresh_token: str


@dataclass(frozen=True)
class SignOutCommand:
    user_id: int
    refresh_token: str
    access_token_id: str
    access_token_expires_at: datetime


@dataclass(frozen=True)
class CompleteWebSignInCommand:
    provider: SocialProvider
    code: str
    nonce: str


@dataclass(frozen=True)
class SignOutWebCommand:
    refresh_token: str | None
    access_token: str | None
