from dataclasses import dataclass
from datetime import date

from arttrip.application.domain.curation.refresh_cycle import RefreshCycle
from arttrip.application.domain.curation.sort_type import SortType
from arttrip.application.domain.exhibit.exhibit_status import ExhibitStatus
from arttrip.application.port.input.exhibit.results import ExhibitSummary
from arttrip.application.port.input.pagination import CursorPage


@dataclass(frozen=True)
class CurationDetail:
    curation_id: int
    title: str
    page: CursorPage[ExhibitSummary]


@dataclass(frozen=True)
class CurationSummary:
    curation_id: int
    title: str
    exhibits: tuple[ExhibitSummary, ...]


@dataclass(frozen=True)
class CurationSearchItem:
    curation_id: int
    title: str
    exhibit_count: int
    created_at: date
    visible_from: date
    visible_to: date
    active: bool


@dataclass(frozen=True)
class ManagedCurationExhibit:
    exhibit_id: int
    title: str | None
    poster_url: str | None
    status: ExhibitStatus
    start_date: date | None
    end_date: date | None
    hall_name: str


@dataclass(frozen=True)
class ManagedCuration:
    curation_id: int
    title: str
    refresh_cycle: RefreshCycle
    sort_type: SortType
    visible_from: date
    visible_to: date
    active: bool
    exhibits: tuple[ManagedCurationExhibit, ...]
