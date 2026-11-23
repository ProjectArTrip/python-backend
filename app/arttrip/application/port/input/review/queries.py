from dataclasses import dataclass


@dataclass(frozen=True)
class ListExhibitReviewsQuery:
    exhibit_id: int
    cursor: int | None
    size: int


@dataclass(frozen=True)
class ListMyReviewsQuery:
    user_id: int
    cursor: int | None
    size: int
