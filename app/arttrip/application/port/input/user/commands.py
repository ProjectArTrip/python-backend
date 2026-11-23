from dataclasses import dataclass
from datetime import datetime

from arttrip.application.domain.user.role import UserRole


@dataclass(frozen=True)
class ChangeNicknameCommand:
    user_id: int
    nickname: str


@dataclass(frozen=True)
class SelectOnboardingRoleCommand:
    user_id: int
    desired_role: UserRole


@dataclass(frozen=True)
class CompleteOnboardingNicknameCommand:
    user_id: int
    nickname: str | None


@dataclass(frozen=True)
class CompleteOnboardingKeywordsCommand:
    user_id: int
    keyword_ids: tuple[int, ...]


@dataclass(frozen=True)
class ReplaceKeywordsCommand:
    user_id: int
    keyword_ids: tuple[int, ...]


@dataclass(frozen=True)
class ChangePushEnabledCommand:
    user_id: int
    enabled: bool


@dataclass(frozen=True)
class RegisterDeviceTokenCommand:
    user_id: int
    token: str


@dataclass(frozen=True)
class ChangeProfileImageCommand:
    user_id: int
    content: bytes
    content_type: str
    extension: str


@dataclass(frozen=True)
class DeleteAccountCommand:
    user_id: int
    refresh_token: str
    access_token_id: str
    access_token_expires_at: datetime
