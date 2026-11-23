from datetime import datetime
from typing import Final

from arttrip.application.domain.artist_application.artist_application_status import (
    ArtistApplicationStatus,
)
from arttrip.application.domain.artist_application.exceptions import (
    ArtistApplicationError,
)
from arttrip.application.util.utc import to_utc

INTRODUCTION_MAX_LENGTH: Final = 1000
PORTFOLIO_URL_MAX_LENGTH: Final = 1024
REJECTION_REASON_MAX_LENGTH: Final = 500
_PORTFOLIO_URL_PREFIX: Final = "https://"


class ArtistApplication:
    def __init__(
        self,
        *,
        id_: int | None,
        user_id: int,
        introduction: str,
        portfolio_url: str | None,
        status: ArtistApplicationStatus,
        rejection_reason: str | None,
        reviewed_by: int | None,
        reviewed_at: datetime | None,
        submitted_at: datetime,
    ) -> None:
        self._id = id_
        self.user_id = user_id
        self.introduction = introduction
        self.portfolio_url = portfolio_url
        self.status = status
        self.rejection_reason = rejection_reason
        self.reviewed_by = reviewed_by
        self.reviewed_at = reviewed_at
        self.submitted_at = to_utc(submitted_at)

    @property
    def id(self) -> int | None:
        return self._id

    @classmethod
    def submit(
        cls,
        *,
        user_id: int,
        introduction: str,
        portfolio_url: str | None,
        now: datetime,
    ) -> "ArtistApplication":
        return cls(
            id_=None,
            user_id=user_id,
            introduction=_validate_introduction(introduction),
            portfolio_url=_validate_portfolio_url(portfolio_url),
            status=ArtistApplicationStatus.PENDING,
            rejection_reason=None,
            reviewed_by=None,
            reviewed_at=None,
            submitted_at=now,
        )

    def approve(self, *, reviewer_id: int, now: datetime) -> None:
        self._ensure_pending()
        self.status = ArtistApplicationStatus.APPROVED
        self.reviewed_by = reviewer_id
        self.reviewed_at = to_utc(now)

    def reject(self, *, reviewer_id: int, reason: str, now: datetime) -> None:
        self._ensure_pending()
        rejection_reason = reason.strip()
        if not 1 <= len(rejection_reason) <= REJECTION_REASON_MAX_LENGTH:
            raise ArtistApplicationError.rejection_reason_required()
        self.status = ArtistApplicationStatus.REJECTED
        self.rejection_reason = rejection_reason
        self.reviewed_by = reviewer_id
        self.reviewed_at = to_utc(now)

    def _ensure_pending(self) -> None:
        if self.status is not ArtistApplicationStatus.PENDING:
            raise ArtistApplicationError.already_reviewed()


def _validate_introduction(raw: str) -> str:
    introduction = raw.strip()
    if not 1 <= len(introduction) <= INTRODUCTION_MAX_LENGTH:
        raise ArtistApplicationError.invalid_introduction()
    return introduction


def _validate_portfolio_url(raw: str | None) -> str | None:
    if raw is None or not raw.strip():
        return None
    portfolio_url = raw.strip()
    if len(portfolio_url) > PORTFOLIO_URL_MAX_LENGTH:
        raise ArtistApplicationError.invalid_portfolio_url()
    if not portfolio_url.lower().startswith(_PORTFOLIO_URL_PREFIX):
        raise ArtistApplicationError.invalid_portfolio_url()
    return portfolio_url
