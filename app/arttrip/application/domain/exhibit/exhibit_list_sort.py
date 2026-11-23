from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class ExhibitListSort(StrEnum):
    POPULAR = "POPULAR"
    LATEST = "LATEST"
    ENDING_SOON = "ENDING_SOON"


@dataclass(frozen=True)
class ExhibitListCursor:
    sort: ExhibitListSort
    value: int | date
    exhibit_id: int
