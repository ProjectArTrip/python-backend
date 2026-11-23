from datetime import datetime
from typing import Final

from pydantic import Field

from arttrip.application.domain.artist_application.artist_application_status import (
    ArtistApplicationStatus,
)
from arttrip.application.domain.user.onboarding_step import OnboardingStep
from arttrip.inbound.http.schemas.base import ApiModel

INTRODUCTION_INPUT_MAX_LENGTH: Final = 2000
PORTFOLIO_URL_INPUT_MAX_LENGTH: Final = 2048


class SubmitArtistApplicationRequest(ApiModel):
    introduction: str = Field(max_length=INTRODUCTION_INPUT_MAX_LENGTH)
    portfolio_url: str | None = Field(
        default=None, max_length=PORTFOLIO_URL_INPUT_MAX_LENGTH
    )


class ArtistApplicationResponse(ApiModel):
    id: int
    status: ArtistApplicationStatus
    introduction: str
    portfolio_url: str | None
    rejection_reason: str | None
    submitted_at: datetime
    reviewed_at: datetime | None


class SubmitArtistApplicationResponse(ArtistApplicationResponse):
    onboarding_step: OnboardingStep
