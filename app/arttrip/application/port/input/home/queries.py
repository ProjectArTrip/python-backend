from dataclasses import dataclass


@dataclass(frozen=True)
class ListTodayExhibitsQuery:
    user_id: int | None


@dataclass(frozen=True)
class ListGenreExhibitsQuery:
    user_id: int | None
    genre_id: int
