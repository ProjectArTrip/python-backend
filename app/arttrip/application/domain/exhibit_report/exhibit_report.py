from datetime import date, datetime
from typing import Final

from arttrip.application.domain.exhibit_report.exceptions import ExhibitReportError
from arttrip.application.domain.exhibit_report.exhibit_report_status import (
    ExhibitReportStatus,
)
from arttrip.application.util.utc import to_utc

TEXT_MAX_LENGTH: Final = 255
DESCRIPTION_MAX_LENGTH: Final = 10000
URL_MAX_LENGTH: Final = 1024
REJECTION_REASON_MAX_LENGTH: Final = 500
_URL_PREFIX: Final = "https://"


class ExhibitReport:
    def __init__(
        self,
        *,
        id_: int | None,
        reporter_id: int,
        title: str,
        country_code: str,
        artist_name: str,
        place_name: str,
        address: str | None,
        start_date: date,
        end_date: date,
        description: str,
        poster_url: str | None,
        source_url: str | None,
        status: ExhibitReportStatus,
        exhibit_id: int | None,
        rejection_reason: str | None,
        reviewed_by: int | None,
        reviewed_at: datetime | None,
        submitted_at: datetime,
    ) -> None:
        self._id = id_
        self.reporter_id = reporter_id
        self.title = title
        self.country_code = country_code
        self.artist_name = artist_name
        self.place_name = place_name
        self.address = address
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.poster_url = poster_url
        self.source_url = source_url
        self.status = status
        self.exhibit_id = exhibit_id
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
        reporter_id: int,
        title: str,
        country_code: str,
        artist_name: str,
        place_name: str,
        address: str | None,
        start_date: date,
        end_date: date,
        description: str,
        poster_url: str | None,
        source_url: str | None,
        now: datetime,
    ) -> "ExhibitReport":
        if start_date > end_date:
            raise ExhibitReportError.invalid_schedule()
        return cls(
            id_=None,
            reporter_id=reporter_id,
            title=_required("전시명", title, TEXT_MAX_LENGTH),
            country_code=country_code,
            artist_name=_required("작가", artist_name, TEXT_MAX_LENGTH),
            place_name=_required("전시 장소", place_name, TEXT_MAX_LENGTH),
            address=_optional("주소", address, TEXT_MAX_LENGTH),
            start_date=start_date,
            end_date=end_date,
            description=_required("전시 설명", description, DESCRIPTION_MAX_LENGTH),
            poster_url=poster_url,
            source_url=_validate_source_url(source_url),
            status=ExhibitReportStatus.PENDING,
            exhibit_id=None,
            rejection_reason=None,
            reviewed_by=None,
            reviewed_at=None,
            submitted_at=now,
        )

    def approve(self, *, exhibit_id: int, reviewer_id: int, now: datetime) -> None:
        self._ensure_pending()
        self.status = ExhibitReportStatus.APPROVED
        self.exhibit_id = exhibit_id
        self.reviewed_by = reviewer_id
        self.reviewed_at = to_utc(now)

    def reject(self, *, reviewer_id: int, reason: str, now: datetime) -> None:
        self._ensure_pending()
        rejection_reason = reason.strip()
        if not 1 <= len(rejection_reason) <= REJECTION_REASON_MAX_LENGTH:
            raise ExhibitReportError.rejection_reason_required()
        self.status = ExhibitReportStatus.REJECTED
        self.rejection_reason = rejection_reason
        self.reviewed_by = reviewer_id
        self.reviewed_at = to_utc(now)

    def _ensure_pending(self) -> None:
        if self.status is not ExhibitReportStatus.PENDING:
            raise ExhibitReportError.already_reviewed()


def _required(field: str, raw: str, max_length: int) -> str:
    value = raw.strip()
    if not value:
        raise ExhibitReportError.required_field_missing(field)
    if len(value) > max_length:
        raise ExhibitReportError.too_long(field, max_length)
    return value


def _optional(field: str, raw: str | None, max_length: int) -> str | None:
    if raw is None or not raw.strip():
        return None
    return _required(field, raw, max_length)


def _validate_source_url(raw: str | None) -> str | None:
    source_url = _optional("공식 출처", raw, URL_MAX_LENGTH)
    if source_url is not None and not source_url.lower().startswith(_URL_PREFIX):
        raise ExhibitReportError.invalid_source_url()
    return source_url
