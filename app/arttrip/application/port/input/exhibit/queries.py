from dataclasses import dataclass

from arttrip.application.domain.exhibit.exhibit_filter import ExhibitFilter
from arttrip.application.domain.exhibit.exhibit_list_sort import (
    ExhibitListCursor,
    ExhibitListSort,
)
from arttrip.application.domain.exhibit.exhibit_search import (
    ExhibitSearch,
    ExhibitSortField,
)
from arttrip.application.util.sort_direction import SortDirection


@dataclass(frozen=True)
class ListExhibitsQuery:
    user_id: int
    criteria: ExhibitFilter
    sort: ExhibitListSort
    cursor: ExhibitListCursor | None
    size: int


@dataclass(frozen=True)
class GetExhibitQuery:
    user_id: int
    exhibit_id: int


@dataclass(frozen=True)
class ListRecentExhibitsQuery:
    user_id: int


@dataclass(frozen=True)
class SearchExhibitsQuery:
    search: ExhibitSearch
    country_name: str | None
    sort: ExhibitSortField
    direction: SortDirection
    page: int
    size: int


@dataclass(frozen=True)
class ListArtistExhibitsQuery:
    artist_id: int
    page: int
    size: int
