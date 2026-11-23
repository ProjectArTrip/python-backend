from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ListTodayExhibitsQuery:
    user_id: int | None
    domestic: bool
    country_code: str | None
    region: str | None


@dataclass(frozen=True)
class ListScheduledExhibitsQuery:
    user_id: int | None
    scheduled_date: date
    domestic: bool
    country_code: str | None
    region: str | None


@dataclass(frozen=True)
class ListPersonalizedExhibitsQuery:
    user_id: int
    domestic: bool
    country_code: str | None
    region: str | None


@dataclass(frozen=True)
class ListGenreExhibitsQuery:
    user_id: int | None
    genre_id: int


@dataclass(frozen=True)
class ListRecentExhibitsQuery:
    user_id: int
