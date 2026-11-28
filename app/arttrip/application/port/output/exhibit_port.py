from abc import ABC, abstractmethod
from collections.abc import Collection, Sequence
from datetime import date

from arttrip.application.domain.exhibit.exhibit import Exhibit
from arttrip.application.domain.exhibit.exhibit_filter import ExhibitFilter
from arttrip.application.domain.exhibit.exhibit_hall import ExhibitHall
from arttrip.application.domain.exhibit.exhibit_list_sort import (
    ExhibitListCursor,
    ExhibitListSort,
)
from arttrip.application.domain.exhibit.exhibit_search import (
    ExhibitSearch,
    ExhibitSortField,
)
from arttrip.application.domain.exhibit.exhibit_status_policy import ExhibitStatusPolicy
from arttrip.application.util.sort_direction import SortDirection

type ExhibitKey = tuple[str, str, date | None]


class ExhibitPort(ABC):
    @abstractmethod
    def find_by_id(self, exhibit_id: int) -> Exhibit | None:
        pass

    @abstractmethod
    def list_page(
        self,
        *,
        criteria: ExhibitFilter,
        sort: ExhibitListSort,
        cursor: ExhibitListCursor | None,
        limit: int,
    ) -> list[tuple[Exhibit, ExhibitListCursor]]:
        pass

    @abstractmethod
    def count(self, *, criteria: ExhibitFilter) -> int:
        pass

    @abstractmethod
    def pick_random(
        self, *, criteria: ExhibitFilter, today: date, pivot: float, limit: int
    ) -> list[Exhibit]:
        pass

    @abstractmethod
    def list_halls_with_ongoing(
        self, *, today: date, limit: int
    ) -> list[tuple[ExhibitHall, int]]:
        pass

    @abstractmethod
    def search_page(
        self,
        *,
        search: ExhibitSearch,
        today: date,
        policy: ExhibitStatusPolicy,
        sort: ExhibitSortField,
        direction: SortDirection,
        offset: int,
        limit: int,
    ) -> list[Exhibit]:
        pass

    @abstractmethod
    def count_search(
        self, *, search: ExhibitSearch, today: date, policy: ExhibitStatusPolicy
    ) -> int:
        pass

    @abstractmethod
    def remove_with_dependents(self, exhibit_id: int) -> None:
        pass

    @abstractmethod
    def find_ids_by_owner(self, owner_id: int) -> list[int]:
        pass

    @abstractmethod
    def add(self, exhibit: Exhibit) -> None:
        pass

    @abstractmethod
    def find_hall_by_name(self, name: str) -> ExhibitHall | None:
        pass

    @abstractmethod
    def exists_same(self, *, hall_id: int, title: str, start_date: date | None) -> bool:
        pass

    @abstractmethod
    def find_by_ids(self, exhibit_ids: Sequence[int]) -> list[Exhibit]:
        pass

    @abstractmethod
    def find_existing_ids(self, exhibit_ids: Collection[int]) -> set[int]:
        pass

    @abstractmethod
    def find_existing_keys(self, keys: Collection[ExhibitKey]) -> set[ExhibitKey]:
        pass

    @abstractmethod
    def find_halls_by_names(self, names: Collection[str]) -> list[ExhibitHall]:
        pass

    @abstractmethod
    def add_all(self, exhibits: Sequence[Exhibit]) -> None:
        pass

    @abstractmethod
    def increment_view_count(self, exhibit_id: int) -> None:
        pass
