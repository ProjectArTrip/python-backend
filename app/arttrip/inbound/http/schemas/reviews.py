from datetime import date, datetime
from typing import Annotated, Final

from fastapi import UploadFile
from pydantic import Field

from arttrip.application.domain.review.review import MAX_IMAGES
from arttrip.application.domain.review.review_status import ReviewStatus
from arttrip.inbound.http.pagination import DEFAULT_PAGE_SIZE, CursorId, PageSize
from arttrip.inbound.http.schemas.base import ApiModel

REVIEW_CONTENT_INPUT_MAX_LENGTH: Final = 2000


class ReviewWriteRequest(ApiModel):
    visit_date: date
    content: str = Field(max_length=REVIEW_CONTENT_INPUT_MAX_LENGTH)
    images: list[UploadFile] = Field(default_factory=list)


class ReviewReviseRequest(ReviewWriteRequest):
    delete_image_ids: list[Annotated[int, Field(gt=0)]] = Field(
        default_factory=list, max_length=MAX_IMAGES
    )


class ReviewImageResponse(ApiModel):
    review_image_id: int
    image_url: str


class ReviewResponse(ApiModel):
    review_id: int
    exhibit_id: int
    content: str
    visit_date: date = Field(alias="date")
    status: ReviewStatus
    rejection_reason: str | None
    images: list[ReviewImageResponse]
    created_at: datetime
    updated_at: datetime


class ReviewPageParams(ApiModel):
    cursor: CursorId = None
    size: PageSize = DEFAULT_PAGE_SIZE


class ExhibitReviewResponse(ApiModel):
    review_id: int
    reviewer_nickname: str
    content: str
    visit_date: date
    images: list[ReviewImageResponse]
    created_at: datetime


class ExhibitReviewListResponse(ApiModel):
    reviews: list[ExhibitReviewResponse]
    total_count: int
    next_cursor: int | None
    has_next: bool


class MyReviewResponse(ApiModel):
    review_id: int
    exhibit_id: int
    exhibit_title: str | None
    poster_url: str | None
    content: str
    visit_date: date
    status: ReviewStatus
    rejection_reason: str | None
    images: list[ReviewImageResponse]
    created_at: datetime


class MyReviewListResponse(ApiModel):
    reviews: list[MyReviewResponse]
    total_count: int
    next_cursor: int | None
    has_next: bool
