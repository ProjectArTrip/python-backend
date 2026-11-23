from typing import Annotated

from pydantic import Field

from arttrip.application.domain.user.onboarding_step import OnboardingStep
from arttrip.application.domain.user.role import UserRole
from arttrip.inbound.http.schemas.base import ApiModel, CaseInsensitive
from arttrip.inbound.http.schemas.users import MAX_KEYWORD_IDS, KeywordId


class SelectOnboardingRoleRequest(ApiModel):
    role: Annotated[UserRole, CaseInsensitive]


class OnboardingProgressResponse(ApiModel):
    onboarding_step: OnboardingStep
    role: UserRole


class CompleteOnboardingNicknameRequest(ApiModel):
    # 생략하면 가입 때 정한 기본 닉네임을 그대로 확정한다
    nickname: str | None = Field(default=None, max_length=50)


class CompleteOnboardingKeywordsRequest(ApiModel):
    keyword_ids: list[KeywordId] = Field(min_length=1, max_length=MAX_KEYWORD_IDS)
