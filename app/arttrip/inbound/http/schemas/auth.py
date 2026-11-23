from typing import Annotated

from pydantic import Field

from arttrip.application.domain.auth.social_provider import SocialProvider
from arttrip.application.domain.user.onboarding_step import OnboardingStep
from arttrip.inbound.http.schemas.base import ApiModel, CaseInsensitive


class SignInRequest(ApiModel):
    provider: Annotated[SocialProvider, CaseInsensitive]
    id_token: str = Field(min_length=1, max_length=8192)


class TokenPairResponse(ApiModel):
    access_token: str
    refresh_token: str


class SignInResponse(TokenPairResponse):
    onboarding_step: OnboardingStep


class RefreshTokenRequest(ApiModel):
    refresh_token: str = Field(min_length=1, max_length=512)
