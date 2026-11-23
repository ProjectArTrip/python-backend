from dataclasses import dataclass, field
from enum import StrEnum

from arttrip.application.domain.exhibit.exhibit_filter import ExhibitFilter
from arttrip.application.domain.exhibit.exhibit_status import ExhibitStatus


class ExhibitSortField(StrEnum):
    CREATED_AT = "CREATED_AT"
    START_DATE = "START_DATE"
    END_DATE = "END_DATE"
    TITLE = "TITLE"


@dataclass(frozen=True)
class ExhibitSearch:
    criteria: ExhibitFilter
    statuses: frozenset[ExhibitStatus] = field(default_factory=frozenset)
    genre_names: frozenset[str] = field(default_factory=frozenset)
    owner_id: int | None = None
