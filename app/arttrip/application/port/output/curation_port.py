from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime

from arttrip.application.domain.curation.curation import Curation
from arttrip.application.domain.exhibit.exhibit import Exhibit
from arttrip.application.domain.exhibit.exhibit_filter import ExhibitFilter


@dataclass(frozen=True)
class CuratedExhibit:
    exhibit: Exhibit
    display_order: int


@dataclass(frozen=True)
class CurationSearchRow:
    curation: Curation
    exhibit_count: int
    created_at: datetime


class CurationPort(ABC):
    @abstractmethod
    def find_by_id(self, curation_id: int) -> Curation | None:
        pass

    @abstractmethod
    def list_exhibits_page(
        self, *, curation_id: int, cursor: int | None, limit: int, today: date
    ) -> list[CuratedExhibit]:
        pass

    @abstractmethod
    def list_visible_ids(self, *, today: date, criteria: ExhibitFilter) -> list[int]:
        pass

    @abstractmethod
    def list_matching_exhibits(
        self, *, curation_id: int, criteria: ExhibitFilter, limit: int, today: date
    ) -> list[Exhibit]:
        pass

    @abstractmethod
    def search_page(
        self, *, keyword: str | None, active: bool | None, offset: int, limit: int
    ) -> list[CurationSearchRow]:
        pass

    @abstractmethod
    def count_search(self, *, keyword: str | None, active: bool | None) -> int:
        pass

    @abstractmethod
    def list_exhibits(self, curation_id: int) -> list[Exhibit]:
        pass

    @abstractmethod
    def add(self, curation: Curation) -> None:
        pass

    @abstractmethod
    def remove(self, curation: Curation) -> None:
        pass
