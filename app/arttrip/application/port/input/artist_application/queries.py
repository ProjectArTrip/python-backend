from dataclasses import dataclass

from arttrip.application.domain.artist_application.artist_application_status import (
    ArtistApplicationStatus,
)


@dataclass(frozen=True)
class ListArtistApplicationsQuery:
    status: ArtistApplicationStatus | None
    cursor: int | None
    size: int
