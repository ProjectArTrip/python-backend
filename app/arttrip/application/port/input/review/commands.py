from dataclasses import dataclass
from datetime import date

from arttrip.application.domain.image.stored_images import UploadedImage


@dataclass(frozen=True)
class WriteReviewCommand:
    user_id: int
    exhibit_id: int
    content: str
    visit_date: date
    images: tuple[UploadedImage, ...]


@dataclass(frozen=True)
class ReviseReviewCommand:
    user_id: int
    review_id: int
    content: str
    visit_date: date
    delete_image_ids: frozenset[int]
    images: tuple[UploadedImage, ...]


@dataclass(frozen=True)
class DeleteReviewCommand:
    user_id: int
    review_id: int
