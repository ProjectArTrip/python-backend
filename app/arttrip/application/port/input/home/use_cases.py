from abc import ABC, abstractmethod

from arttrip.application.port.input.exhibit.results import ExhibitSummary
from arttrip.application.port.input.home.queries import (
    ListGenreExhibitsQuery,
    ListTodayExhibitsQuery,
)
from arttrip.application.port.input.home.results import HomeVenue


class ListTodayExhibitsUseCase(ABC):
    @abstractmethod
    def list_today_exhibits(
        self, query: ListTodayExhibitsQuery
    ) -> tuple[ExhibitSummary, ...]:
        pass


class ListGenreExhibitsUseCase(ABC):
    @abstractmethod
    def list_genre_exhibits(
        self, query: ListGenreExhibitsQuery
    ) -> tuple[ExhibitSummary, ...]:
        pass


class ListHomeVenuesUseCase(ABC):
    @abstractmethod
    def list_home_venues(self) -> tuple[HomeVenue, ...]:
        pass
