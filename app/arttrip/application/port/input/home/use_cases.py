from abc import ABC, abstractmethod

from arttrip.application.port.input.exhibit.results import ExhibitSummary
from arttrip.application.port.input.home.queries import (
    ListGenreExhibitsQuery,
    ListPersonalizedExhibitsQuery,
    ListScheduledExhibitsQuery,
    ListTodayExhibitsQuery,
)


class ListTodayExhibitsUseCase(ABC):
    @abstractmethod
    def list_today_exhibits(
        self, query: ListTodayExhibitsQuery
    ) -> tuple[ExhibitSummary, ...]:
        pass


class ListScheduledExhibitsUseCase(ABC):
    @abstractmethod
    def list_scheduled_exhibits(
        self, query: ListScheduledExhibitsQuery
    ) -> tuple[ExhibitSummary, ...]:
        pass


class ListPersonalizedExhibitsUseCase(ABC):
    @abstractmethod
    def list_personalized_exhibits(
        self, query: ListPersonalizedExhibitsQuery
    ) -> tuple[ExhibitSummary, ...]:
        pass


class ListGenreExhibitsUseCase(ABC):
    @abstractmethod
    def list_genre_exhibits(
        self, query: ListGenreExhibitsQuery
    ) -> tuple[ExhibitSummary, ...]:
        pass
