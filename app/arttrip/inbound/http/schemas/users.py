from typing import Annotated, Final

from pydantic import Field

from arttrip.application.domain.user.onboarding_step import OnboardingStep
from arttrip.application.domain.user.role import UserRole
from arttrip.inbound.http.schemas.base import ApiModel

MAX_KEYWORD_IDS: Final = 50
DEVICE_TOKEN_MAX_LENGTH: Final = 255
KeywordId = Annotated[int, Field(gt=0)]


class UserProfileResponse(ApiModel):
    nickname: str
    email: str | None
    role: UserRole
    onboarding_step: OnboardingStep
    push_enabled: bool
    profile_image_url: str | None


class ChangeNicknameRequest(ApiModel):
    nickname: str = Field(max_length=50)


class ChangeNicknameResponse(ApiModel):
    nickname: str
    onboarding_step: OnboardingStep


class ReplaceKeywordsRequest(ApiModel):
    keyword_ids: list[KeywordId] = Field(min_length=1, max_length=MAX_KEYWORD_IDS)


class ReplaceKeywordsResponse(ApiModel):
    keyword_ids: list[int]
    onboarding_step: OnboardingStep


class ChangePushEnabledRequest(ApiModel):
    enabled: bool


class PushEnabledResponse(ApiModel):
    push_enabled: bool


class RegisterDeviceTokenRequest(ApiModel):
    token: str = Field(min_length=1, max_length=DEVICE_TOKEN_MAX_LENGTH)


class ProfileImageResponse(ApiModel):
    profile_image_url: str
