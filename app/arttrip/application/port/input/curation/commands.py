from dataclasses import dataclass
from datetime import date

from arttrip.application.domain.curation.refresh_cycle import RefreshCycle
from arttrip.application.domain.curation.sort_type import SortType


@dataclass(frozen=True)
class CreateCurationCommand:
    title: str
    refresh_cycle: RefreshCycle
    sort_type: SortType
    visible_from: date
    visible_to: date
    active: bool
    exhibit_ids: tuple[int, ...]


@dataclass(frozen=True)
class UpdateCurationCommand:
    curation_id: int
    title: str
    refresh_cycle: RefreshCycle
    sort_type: SortType
    visible_from: date
    visible_to: date
    active: bool
    exhibit_ids: tuple[int, ...]
