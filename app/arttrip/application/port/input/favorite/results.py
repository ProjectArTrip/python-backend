from dataclasses import dataclass

from arttrip.application.port.input.exhibit.results import ExhibitSummary
from arttrip.application.port.input.pagination import CursorPage


@dataclass(frozen=True)
class ListFavoritesResult:
    page: CursorPage[ExhibitSummary]
    total_count: int
