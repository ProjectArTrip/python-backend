from abc import ABC, abstractmethod

from arttrip.application.port.input.artist_application.commands import (
    ApproveArtistApplicationCommand,
    RejectArtistApplicationCommand,
    SubmitArtistApplicationCommand,
)
from arttrip.application.port.input.artist_application.queries import (
    ListArtistApplicationsQuery,
)
from arttrip.application.port.input.artist_application.results import (
    ArtistApplicationView,
    ManagedArtistApplication,
    SubmitArtistApplicationResult,
)
from arttrip.application.port.input.pagination import CursorPage


class SubmitArtistApplicationUseCase(ABC):
    @abstractmethod
    def submit_artist_application(
        self, command: SubmitArtistApplicationCommand
    ) -> SubmitArtistApplicationResult:
        pass


class GetLatestArtistApplicationUseCase(ABC):
    @abstractmethod
    def get_latest_artist_application(self, user_id: int) -> ArtistApplicationView:
        pass


class ListArtistApplicationsUseCase(ABC):
    @abstractmethod
    def list_artist_applications(
        self, query: ListArtistApplicationsQuery
    ) -> CursorPage[ArtistApplicationView]:
        pass


class ApproveArtistApplicationUseCase(ABC):
    @abstractmethod
    def approve_artist_application(
        self, command: ApproveArtistApplicationCommand
    ) -> ArtistApplicationView:
        pass


class RejectArtistApplicationUseCase(ABC):
    @abstractmethod
    def reject_artist_application(
        self, command: RejectArtistApplicationCommand
    ) -> ArtistApplicationView:
        pass


class GetManagedArtistApplicationUseCase(ABC):
    @abstractmethod
    def get_managed_artist_application(
        self, application_id: int
    ) -> ManagedArtistApplication:
        pass
