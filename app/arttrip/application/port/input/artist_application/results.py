from dataclasses import dataclass
from datetime import datetime

from arttrip.application.domain.artist_application.artist_application_status import (
    ArtistApplicationStatus,
)
from arttrip.application.domain.user.onboarding_step import OnboardingStep


@dataclass(frozen=True)
class ArtistApplicationView:
    application_id: int
    status: ArtistApplicationStatus
    introduction: str
    portfolio_url: str | None
    rejection_reason: str | None
    submitted_at: datetime
    reviewed_at: datetime | None


@dataclass(frozen=True)
class SubmitArtistApplicationResult:
    application: ArtistApplicationView
    onboarding_step: OnboardingStep


@dataclass(frozen=True)
class ManagedArtistApplication:
    application: ArtistApplicationView
    applicant_id: int
    applicant_nickname: str
    reviewed_by: int | None
