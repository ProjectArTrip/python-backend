from datetime import UTC, datetime
from typing import Final

from arttrip.application.domain.exhibit.exceptions import ExhibitError
from arttrip.application.domain.image.stored_images import (
    delete_all_quietly,
    upload_all,
)
from arttrip.application.domain.review.exceptions import ReviewError
from arttrip.application.domain.review.review import MAX_IMAGES, Review
from arttrip.application.port.input.pagination import CursorPage
from arttrip.application.port.input.review.commands import (
    DeleteReviewCommand,
    ReviseReviewCommand,
    WriteReviewCommand,
)
from arttrip.application.port.input.review.queries import (
    ListExhibitReviewsQuery,
    ListMyReviewsQuery,
)
from arttrip.application.port.input.review.results import (
    ExhibitReviewItem,
    ListExhibitReviewsResult,
    ListMyReviewsResult,
    MyReviewItem,
    ReviewImageView,
    ReviewView,
)
from arttrip.application.port.input.review.use_cases import (
    DeleteReviewUseCase,
    ListExhibitReviewsUseCase,
    ListMyReviewsUseCase,
    ReviseReviewUseCase,
    WriteReviewUseCase,
)
from arttrip.application.port.output.image_storage_port import ImageStoragePort
from arttrip.application.port.output.review_port import AuthoredReview, WrittenReview
from arttrip.application.port.output.unit_of_work import UnitOfWork
from arttrip.application.util.service_date import to_service_date

REVIEW_IMAGE_FOLDER: Final = "reviews"


class WriteReviewService(WriteReviewUseCase):
    def __init__(self, *, uow: UnitOfWork, storage: ImageStoragePort) -> None:
        self._uow = uow
        self._storage = storage

    def write_review(self, command: WriteReviewCommand) -> ReviewView:
        if len(command.images) > MAX_IMAGES:
            raise ReviewError.too_many_images()
        now = datetime.now(UTC)
        keys = upload_all(self._storage, command.images, folder=REVIEW_IMAGE_FOLDER)
        try:
            with self._uow as uow:
                if uow.exhibits.find_by_id(command.exhibit_id) is None:
                    raise ExhibitError.not_found()
                if uow.reviews.exists_by_user_and_exhibit(
                    user_id=command.user_id, exhibit_id=command.exhibit_id
                ):
                    raise ReviewError.already_written()
                review = Review.write(
                    user_id=command.user_id,
                    exhibit_id=command.exhibit_id,
                    content=command.content,
                    visit_date=command.visit_date,
                    image_keys=keys,
                    banned_words=uow.banned_words.find_active_words(),
                    today=to_service_date(now),
                    now=now,
                )
                uow.reviews.add(review)
        except Exception:
            delete_all_quietly(self._storage, keys)
            raise
        return to_view(review, self._storage)


class ReviseReviewService(ReviseReviewUseCase):
    def __init__(self, *, uow: UnitOfWork, storage: ImageStoragePort) -> None:
        self._uow = uow
        self._storage = storage

    def revise_review(self, command: ReviseReviewCommand) -> ReviewView:
        if len(command.images) > MAX_IMAGES:
            raise ReviewError.too_many_images()
        now = datetime.now(UTC)
        new_keys = upload_all(self._storage, command.images, folder=REVIEW_IMAGE_FOLDER)
        try:
            with self._uow as uow:
                review = _load(uow, command.review_id)
                removed_keys = review.revise(
                    editor_id=command.user_id,
                    content=command.content,
                    visit_date=command.visit_date,
                    delete_image_ids=command.delete_image_ids,
                    new_image_keys=new_keys,
                    banned_words=uow.banned_words.find_active_words(),
                    today=to_service_date(now),
                    now=now,
                )
        except Exception:
            delete_all_quietly(self._storage, new_keys)
            raise
        delete_all_quietly(self._storage, removed_keys)
        return to_view(review, self._storage)


class DeleteReviewService(DeleteReviewUseCase):
    def __init__(self, *, uow: UnitOfWork, storage: ImageStoragePort) -> None:
        self._uow = uow
        self._storage = storage

    def delete_review(self, command: DeleteReviewCommand) -> None:
        with self._uow as uow:
            review = _load(uow, command.review_id)
            review.ensure_written_by(command.user_id)
            keys = review.image_keys()
            uow.reviews.remove(review)
        delete_all_quietly(self._storage, keys)


class ListExhibitReviewsService(ListExhibitReviewsUseCase):
    def __init__(self, *, uow: UnitOfWork, storage: ImageStoragePort) -> None:
        self._uow = uow
        self._storage = storage

    def list_exhibit_reviews(
        self, query: ListExhibitReviewsQuery
    ) -> ListExhibitReviewsResult:
        with self._uow as uow:
            if uow.exhibits.find_by_id(query.exhibit_id) is None:
                raise ExhibitError.not_found()
            rows = uow.reviews.list_approved_page(
                exhibit_id=query.exhibit_id,
                cursor=query.cursor,
                limit=query.size + 1,
            )
            has_next = len(rows) > query.size
            page_rows = rows[: query.size]
            next_cursor = page_rows[-1].review.id if has_next else None
            total_count = uow.reviews.count_approved(exhibit_id=query.exhibit_id)
            return ListExhibitReviewsResult(
                page=CursorPage(
                    items=tuple(_to_item(row, self._storage) for row in page_rows),
                    next_cursor=next_cursor,
                ),
                total_count=total_count,
            )


class ListMyReviewsService(ListMyReviewsUseCase):
    def __init__(self, *, uow: UnitOfWork, storage: ImageStoragePort) -> None:
        self._uow = uow
        self._storage = storage

    def list_my_reviews(self, query: ListMyReviewsQuery) -> ListMyReviewsResult:
        with self._uow as uow:
            rows = uow.reviews.list_page_by_user(
                user_id=query.user_id, cursor=query.cursor, limit=query.size + 1
            )
            has_next = len(rows) > query.size
            page_rows = rows[: query.size]
            next_cursor = page_rows[-1].review.id if has_next else None
            total_count = uow.reviews.count_by_user(user_id=query.user_id)
            return ListMyReviewsResult(
                page=CursorPage(
                    items=tuple(_to_my_item(row, self._storage) for row in page_rows),
                    next_cursor=next_cursor,
                ),
                total_count=total_count,
            )


def to_view(review: Review, storage: ImageStoragePort) -> ReviewView:
    review_id = review.id
    if review_id is None:
        raise RuntimeError("review must have an id after it is stored")
    return ReviewView(
        review_id=review_id,
        exhibit_id=review.exhibit_id,
        content=review.content,
        visit_date=review.visit_date,
        status=review.status,
        rejection_reason=review.rejection_reason,
        images=_image_views(review, storage),
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


def _image_views(
    review: Review, storage: ImageStoragePort
) -> tuple[ReviewImageView, ...]:
    return tuple(
        ReviewImageView(image_id=image.id, url=storage.public_url(image.image_key))
        for image in review.images
        if image.id is not None
    )


def _load(uow: UnitOfWork, review_id: int) -> Review:
    review = uow.reviews.find_by_id(review_id)
    if review is None:
        raise ReviewError.not_found()
    return review


def _to_item(row: AuthoredReview, storage: ImageStoragePort) -> ExhibitReviewItem:
    review = row.review
    review_id = review.id
    if review_id is None:
        raise RuntimeError("listed review must have an id")
    return ExhibitReviewItem(
        review_id=review_id,
        reviewer_nickname=row.author_nickname,
        content=review.content,
        visit_date=review.visit_date,
        images=_image_views(review, storage),
        created_at=review.created_at,
    )


def _to_my_item(row: WrittenReview, storage: ImageStoragePort) -> MyReviewItem:
    review = row.review
    review_id = review.id
    if review_id is None:
        raise RuntimeError("listed review must have an id")
    return MyReviewItem(
        review_id=review_id,
        exhibit_id=review.exhibit_id,
        exhibit_title=row.exhibit_title,
        poster_url=row.poster_url,
        content=review.content,
        visit_date=review.visit_date,
        status=review.status,
        rejection_reason=review.rejection_reason,
        images=_image_views(review, storage),
        created_at=review.created_at,
    )
