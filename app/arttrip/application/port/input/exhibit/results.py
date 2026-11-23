from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from arttrip.application.domain.exhibit.exhibit_list_sort import ExhibitListCursor
from arttrip.application.domain.exhibit.exhibit_status import ExhibitStatus
from arttrip.application.port.input.exhibit.commands import ExhibitImportRow


@dataclass(frozen=True)
class ExhibitHallView:
    name: str
    address: str | None
    phone: str | None
    homepage_url: str | None
    opening_hours: str | None
    closed_days: str | None
    region: str
    country_code: str
    latitude: Decimal
    longitude: Decimal


@dataclass(frozen=True)
class ExhibitHallSummary:
    name: str
    region: str
    country_code: str


@dataclass(frozen=True)
class ExhibitDetail:
    exhibit_id: int
    title: str | None
    description: str | None
    poster_url: str | None
    ticket_url: str | None
    status: ExhibitStatus
    start_date: date | None
    end_date: date | None
    hall: ExhibitHallView
    is_favorite: bool
    review_count: int


@dataclass(frozen=True)
class ExhibitSummary:
    exhibit_id: int
    title: str | None
    poster_url: str | None
    status: ExhibitStatus
    start_date: date | None
    end_date: date | None
    hall: ExhibitHallSummary
    is_favorite: bool


@dataclass(frozen=True)
class ExhibitSearchItem:
    exhibit_id: int
    title: str | None
    start_date: date | None
    end_date: date | None
    country_name: str
    region: str
    genres: tuple[str, ...]
    status: ExhibitStatus
    hall_name: str


@dataclass(frozen=True)
class ManagedExhibit:
    exhibit_id: int
    title: str | None
    description: str | None
    poster_url: str | None
    ticket_url: str | None
    start_date: date | None
    end_date: date | None
    status: ExhibitStatus
    hall_id: int
    hall_name: str
    country_name: str
    region: str
    address: str | None
    opening_hours: str | None
    phone: str | None
    latitude: Decimal
    longitude: Decimal
    is_domestic: bool
    genres: tuple[str, ...]
    styles: tuple[str, ...]


@dataclass(frozen=True)
class ExhibitImportGuide:
    country_names: tuple[str, ...]
    region_names: tuple[str, ...]
    genre_names: tuple[str, ...]
    style_names: tuple[str, ...]


@dataclass(frozen=True)
class ExhibitImportIssue:
    row_number: int
    field: str | None
    message: str


@dataclass(frozen=True)
class ExhibitImportCandidate:
    row: ExhibitImportRow
    is_domestic: bool


@dataclass(frozen=True)
class ExhibitImportPreview:
    candidates: tuple[ExhibitImportCandidate, ...]
    duplicate_row_numbers: tuple[int, ...]
    issues: tuple[ExhibitImportIssue, ...]


@dataclass(frozen=True)
class ExhibitImportResult:
    exhibit_ids: tuple[int, ...]
    skipped_row_numbers: tuple[int, ...]
    issues: tuple[ExhibitImportIssue, ...]


@dataclass(frozen=True)
class ExhibitPage:
    items: tuple[ExhibitSummary, ...]
    next_cursor: ExhibitListCursor | None

    @property
    def has_next(self) -> bool:
        return self.next_cursor is not None
