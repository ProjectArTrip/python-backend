from collections.abc import Collection, Sequence
from datetime import date, datetime
from typing import Final

from arttrip.application.domain.review.banned_words import contains_banned_word
from arttrip.application.domain.review.exceptions import ReviewError
from arttrip.application.domain.review.review_image import ReviewImage
from arttrip.application.domain.review.review_status import ReviewStatus
from arttrip.application.util.utc import to_utc

CONTENT_MIN_LENGTH: Final = 20
CONTENT_MAX_LENGTH: Final = 500
MAX_IMAGES: Final = 4
REJECTION_REASON_MAX_LENGTH: Final = 200


class Review:
    def __init__(
        self,
        *,
        id_: int | None,
        user_id: int,
        exhibit_id: int,
        content: str,
        visit_date: date,
        status: ReviewStatus,
        rejection_reason: str | None,
        reviewed_by: int | None,
        reviewed_at: datetime | None,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        self._id = id_
        self.user_id = user_id
        self.exhibit_id = exhibit_id
        self.content = content
        self.visit_date = visit_date
        self.status = status
        self.rejection_reason = rejection_reason
        self.reviewed_by = reviewed_by
        self.reviewed_at = reviewed_at
        self.created_at = to_utc(created_at)
        self.updated_at = to_utc(updated_at)
        self.images: list[ReviewImage] = []

    @property
    def id(self) -> int | None:
        return self._id

    @classmethod
    def write(
        cls,
        *,
        user_id: int,
        exhibit_id: int,
        content: str,
        visit_date: date,
        image_keys: Sequence[str],
        banned_words: Collection[str],
        today: date,
        now: datetime,
    ) -> "Review":
        review = cls(
            id_=None,
            user_id=user_id,
            exhibit_id=exhibit_id,
            content=_validate_content(content, banned_words),
            visit_date=_validate_visit_date(visit_date, today=today),
            status=ReviewStatus.PENDING,
            rejection_reason=None,
            reviewed_by=None,
            reviewed_at=None,
            created_at=now,
            updated_at=now,
        )
        review._replace_images(kept=[], new_image_keys=image_keys)
        return review

    def revise(
        self,
        *,
        editor_id: int,
        content: str,
        visit_date: date,
        delete_image_ids: Collection[int],
        new_image_keys: Sequence[str],
        banned_words: Collection[str],
        today: date,
        now: datetime,
    ) -> list[str]:
        self.ensure_written_by(editor_id)

        validated_content = _validate_content(content, banned_words)

        validated_visit_date = _validate_visit_date(visit_date, today=today)

        own_image_ids = {image.id for image in self.images}

        if not set(delete_image_ids) <= own_image_ids:
            raise ReviewError.image_not_found()
        removed = [image for image in self.images if image.id in delete_image_ids]
        kept = [image for image in self.images if image.id not in delete_image_ids]
        if len(kept) + len(new_image_keys) > MAX_IMAGES:
            raise ReviewError.too_many_images()

        self.content = validated_content
        self.visit_date = validated_visit_date
        self._replace_images(kept=kept, new_image_keys=new_image_keys)
        if self.status is ReviewStatus.REJECTED:
            self.status = ReviewStatus.PENDING
            self.rejection_reason = None
            self.reviewed_by = None
            self.reviewed_at = None
        self.updated_at = to_utc(now)
        return [image.image_key for image in removed]

    def approve(self, *, reviewer_id: int, now: datetime) -> None:
        self._ensure_pending()
        self.status = ReviewStatus.APPROVED
        self.reviewed_by = reviewer_id
        self.reviewed_at = to_utc(now)

    def reject(self, *, reviewer_id: int, reason: str, now: datetime) -> None:
        self._ensure_pending()
        rejection_reason = reason.strip()
        if not 1 <= len(rejection_reason) <= REJECTION_REASON_MAX_LENGTH:
            raise ReviewError.rejection_reason_required()
        self.status = ReviewStatus.REJECTED
        self.rejection_reason = rejection_reason
        self.reviewed_by = reviewer_id
        self.reviewed_at = to_utc(now)

    def ensure_written_by(self, user_id: int) -> None:
        if self.user_id != user_id:
            raise ReviewError.not_found()

    def ensure_readable_by(self, user_id: int | None) -> None:
        if self.status is not ReviewStatus.APPROVED and self.user_id != user_id:
            raise ReviewError.not_found()

    def image_keys(self) -> list[str]:
        return [image.image_key for image in self.images]

    def _replace_images(
        self, *, kept: Sequence[ReviewImage], new_image_keys: Sequence[str]
    ) -> None:
        if len(kept) + len(new_image_keys) > MAX_IMAGES:
            raise ReviewError.too_many_images()
        added = [
            ReviewImage(id_=None, image_key=key, display_order=0)
            for key in new_image_keys
        ]
        self.images = [*kept, *added]
        for order, image in enumerate(self.images, start=1):
            image.display_order = order

    def _ensure_pending(self) -> None:
        if self.status is not ReviewStatus.PENDING:
            raise ReviewError.not_pending()


def _validate_content(raw: str, banned_words: Collection[str]) -> str:
    content = raw.strip()
    if not CONTENT_MIN_LENGTH <= len(content) <= CONTENT_MAX_LENGTH:
        raise ReviewError.invalid_content()
    if contains_banned_word(content, banned_words):
        raise ReviewError.banned_word_included()
    return content


def _validate_visit_date(visit_date: date, *, today: date) -> date:
    if visit_date > today:
        raise ReviewError.future_visit_date()
    return visit_date
