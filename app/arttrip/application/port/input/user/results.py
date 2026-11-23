from dataclasses import dataclass

from arttrip.application.domain.user.onboarding_step import OnboardingStep
from arttrip.application.domain.user.role import UserRole


@dataclass(frozen=True)
class UserProfile:
    nickname: str
    email: str | None
    role: UserRole
    onboarding_step: OnboardingStep
    push_enabled: bool
    profile_image_url: str | None


@dataclass(frozen=True)
class ChangeNicknameResult:
    nickname: str
    onboarding_step: OnboardingStep


@dataclass(frozen=True)
class OnboardingProgress:
    onboarding_step: OnboardingStep
    role: UserRole


@dataclass(frozen=True)
class ReplaceKeywordsResult:
    keyword_ids: tuple[int, ...]
    onboarding_step: OnboardingStep


@dataclass(frozen=True)
class ProfileImage:
    url: str
