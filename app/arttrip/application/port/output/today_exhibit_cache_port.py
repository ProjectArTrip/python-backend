from abc import ABC, abstractmethod
from datetime import date

from arttrip.application.domain.exhibit.exhibit_filter import ExhibitFilter


class TodayExhibitCachePort(ABC):
    @abstractmethod
    def find(self, *, day: date, criteria: ExhibitFilter) -> list[int] | None:
        pass

    @abstractmethod
    def save_if_absent(
        self, *, day: date, criteria: ExhibitFilter, exhibit_ids: list[int]
    ) -> list[int]:
        pass
