from dataclasses import dataclass, field
from datetime import date

from arttrip.application.domain.exhibit.exceptions import ExhibitError
from arttrip.application.domain.exhibit.exhibit_hall import DEFAULT_COUNTRY_CODE


@dataclass(frozen=True)
class ExhibitFilter:
    search_text: str | None = None
    period_start: date | None = None
    period_end: date | None = None
    domestic: bool | None = None
    country_code: str | None = None
    regions: frozenset[str] = field(default_factory=frozenset)
    genre_ids: frozenset[int] = field(default_factory=frozenset)
    style_ids: frozenset[int] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if self.domestic is False and self.regions:
            raise ExhibitError.region_requires_domestic()
        if self.domestic is not None and self.country_code is not None:
            is_korea = self.country_code == DEFAULT_COUNTRY_CODE
            if is_korea is not self.domestic:
                raise ExhibitError.country_conflicts_with_domestic()
        if (
            self.period_start is not None
            and self.period_end is not None
            and self.period_start > self.period_end
        ):
            raise ExhibitError.invalid_period()
