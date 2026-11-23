from dataclasses import dataclass
from datetime import date, datetime

from arttrip.application.domain.review.review_status import ReviewStatus
from arttrip.application.port.input.pagination import CursorPage


@dataclass(frozen=True)
class ReviewImageView:
    image_id: int
    url: str


@dataclass(frozen=True)
class ReviewView:
    review_id: int
    exhibit_id: int
    content: str
    visit_date: date
    status: ReviewStatus
    rejection_reason: str | None
    images: tuple[ReviewImageView, ...]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ExhibitReviewItem:
    review_id: int
    reviewer_nickname: str
    content: str
    visit_date: date
    images: tuple[ReviewImageView, ...]
    created_at: datetime


@dataclass(frozen=True)
class ListExhibitReviewsResult:
    page: CursorPage[ExhibitReviewItem]
    total_count: int


@dataclass(frozen=True)
class MyReviewItem:
    review_id: int
    exhibit_id: int
    exhibit_title: str | None
    poster_url: str | None
    content: str
    visit_date: date
    status: ReviewStatus
    rejection_reason: str | None
    images: tuple[ReviewImageView, ...]
    created_at: datetime


@dataclass(frozen=True)
class ListMyReviewsResult:
    page: CursorPage[MyReviewItem]
    total_count: int
