from datetime import datetime
from typing import Final

from pydantic import Field

from arttrip.application.domain.artist_application.artist_application_status import (
    ArtistApplicationStatus,
)
from arttrip.inbound.http.schemas.base import ApiModel

REJECTION_REASON_INPUT_MAX_LENGTH: Final = 1000


class RejectArtistApplicationRequest(ApiModel):
    reason: str = Field(max_length=REJECTION_REASON_INPUT_MAX_LENGTH)


class AdminArtistApplicationResponse(ApiModel):
    id: int
    status: ArtistApplicationStatus
    introduction: str
    portfolio_url: str | None
    rejection_reason: str | None
    submitted_at: datetime
    reviewed_at: datetime | None


class AdminArtistApplicationListResponse(ApiModel):
    requests: list[AdminArtistApplicationResponse]
    next_cursor: int | None
    has_next: bool


class ApplicantResponse(ApiModel):
    id: int
    nickname: str


class AdminArtistApplicationDetailResponse(ApiModel):
    application: AdminArtistApplicationResponse
    applicant: ApplicantResponse
    reviewed_by: int | None
