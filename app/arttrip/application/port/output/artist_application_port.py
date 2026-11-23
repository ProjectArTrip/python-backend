from abc import ABC, abstractmethod

from arttrip.application.domain.artist_application.artist_application import (
    ArtistApplication,
)
from arttrip.application.domain.artist_application.artist_application_status import (
    ArtistApplicationStatus,
)


class ArtistApplicationPort(ABC):
    @abstractmethod
    def add(self, application: ArtistApplication) -> None:
        pass

    @abstractmethod
    def find_pending_by_user_id(self, user_id: int) -> ArtistApplication | None:
        pass

    @abstractmethod
    def find_latest_by_user_id(self, user_id: int) -> ArtistApplication | None:
        pass

    @abstractmethod
    def find_by_id(self, application_id: int) -> ArtistApplication | None:
        pass

    @abstractmethod
    def list_page(
        self,
        *,
        status: ArtistApplicationStatus | None,
        cursor: int | None,
        limit: int,
    ) -> list[ArtistApplication]:
        pass
