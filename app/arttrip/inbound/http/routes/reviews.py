from typing import Annotated

from fastapi import APIRouter, File, Path, UploadFile
from fastapi.params import Form, Query

from arttrip.application.domain.exhibit.exceptions import ExhibitError
from arttrip.application.domain.image.exceptions import ImageError
from arttrip.application.domain.image.stored_images import UploadedImage
from arttrip.application.domain.review.exceptions import ReviewError
from arttrip.application.domain.review.review import MAX_IMAGES
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
    MyReviewItem,
    ReviewImageView,
    ReviewView,
)
from arttrip.common import settings
from arttrip.inbound.http.dependencies.auth import CurrentUserDep
from arttrip.inbound.http.dependencies.review import (
    DeleteReviewUseCaseDep,
    ListExhibitReviewsUseCaseDep,
    ListMyReviewsUseCaseDep,
    ReviseReviewUseCaseDep,
    WriteReviewUseCaseDep,
)
from arttrip.inbound.http.image_upload import read_image_upload
from arttrip.inbound.http.openapi import AUTHENTICATION_ERRORS, error_responses
from arttrip.inbound.http.schemas.reviews import (
    ExhibitReviewListResponse,
    ExhibitReviewResponse,
    MyReviewListResponse,
    MyReviewResponse,
    ReviewImageResponse,
    ReviewPageParams,
    ReviewResponse,
    ReviewReviseRequest,
    ReviewWriteRequest,
)

router = APIRouter()

ExhibitIdParam = Annotated[int, Path(gt=0)]
ReviewIdParam = Annotated[int, Path(gt=0)]
ImagesPart = Annotated[list[UploadFile] | None, File()]

REVIEW_INPUT_ERRORS = (
    ReviewError.invalid_content,
    ReviewError.banned_word_included,
    ReviewError.future_visit_date,
    ReviewError.too_many_images,
    ImageError.storage_unavailable,
)
WriteForm = Annotated[ReviewWriteRequest, Form()]
ReviseForm = Annotated[ReviewReviseRequest, Form()]


@router.post(
    "/exhibits/{exhibit_id}/reviews",
    status_code=201,
    response_model=ReviewResponse,
    responses=error_responses(
        *AUTHENTICATION_ERRORS,
        *REVIEW_INPUT_ERRORS,
        ExhibitError.not_found,
        ReviewError.already_written,
    ),
)
def write_review(
    exhibit_id: ExhibitIdParam,
    body: WriteForm,
    current_user: CurrentUserDep,
    use_case: WriteReviewUseCaseDep,
) -> ReviewResponse:
    view = use_case.write_review(
        WriteReviewCommand(
            user_id=current_user.user_id,
            exhibit_id=exhibit_id,
            content=body.content,
            visit_date=body.visit_date,
            images=_read_images(body.images),
        )
    )
    return _to_response(view)


@router.get(
    "/exhibits/{exhibit_id}/reviews",
    response_model=ExhibitReviewListResponse,
    responses=error_responses(ExhibitError.not_found),
)
def list_exhibit_reviews(
    exhibit_id: ExhibitIdParam,
    use_case: ListExhibitReviewsUseCaseDep,
    params: Annotated[ReviewPageParams, Query()],
) -> ExhibitReviewListResponse:
    result = use_case.list_exhibit_reviews(
        ListExhibitReviewsQuery(
            exhibit_id=exhibit_id, cursor=params.cursor, size=params.size
        )
    )
    return ExhibitReviewListResponse(
        reviews=[_to_exhibit_review_response(item) for item in result.page.items],
        total_count=result.total_count,
        next_cursor=result.page.next_cursor,
        has_next=result.page.has_next,
    )


@router.get(
    "/users/me/reviews",
    response_model=MyReviewListResponse,
    responses=error_responses(*AUTHENTICATION_ERRORS),
)
def list_my_reviews(
    current_user: CurrentUserDep,
    use_case: ListMyReviewsUseCaseDep,
    params: Annotated[ReviewPageParams, Query()],
) -> MyReviewListResponse:
    result = use_case.list_my_reviews(
        ListMyReviewsQuery(
            user_id=current_user.user_id, cursor=params.cursor, size=params.size
        )
    )
    return MyReviewListResponse(
        reviews=[_to_my_review_response(item) for item in result.page.items],
        total_count=result.total_count,
        next_cursor=result.page.next_cursor,
        has_next=result.page.has_next,
    )


@router.patch(
    "/reviews/{review_id}",
    response_model=ReviewResponse,
    responses=error_responses(
        *AUTHENTICATION_ERRORS,
        *REVIEW_INPUT_ERRORS,
        ReviewError.not_found,
        ReviewError.image_not_found,
    ),
)
def revise_review(
    review_id: ReviewIdParam,
    body: ReviseForm,
    current_user: CurrentUserDep,
    use_case: ReviseReviewUseCaseDep,
) -> ReviewResponse:
    view = use_case.revise_review(
        ReviseReviewCommand(
            user_id=current_user.user_id,
            review_id=review_id,
            content=body.content,
            visit_date=body.visit_date,
            delete_image_ids=frozenset(body.delete_image_ids),
            images=_read_images(body.images),
        )
    )
    return _to_response(view)


@router.delete(
    "/reviews/{review_id}",
    status_code=204,
    responses=error_responses(*AUTHENTICATION_ERRORS, ReviewError.not_found),
)
def delete_review(
    review_id: ReviewIdParam,
    current_user: CurrentUserDep,
    use_case: DeleteReviewUseCaseDep,
) -> None:
    use_case.delete_review(
        DeleteReviewCommand(user_id=current_user.user_id, review_id=review_id)
    )


def _read_images(files: list[UploadFile] | None) -> tuple[UploadedImage, ...]:
    uploads = files or []
    if len(uploads) > MAX_IMAGES:
        raise ReviewError.too_many_images()
    limits = settings.image
    prepared = [
        read_image_upload(
            file,
            max_bytes=limits.max_bytes,
            max_pixels=limits.max_pixels,
            max_side=limits.max_side,
            quality=limits.jpeg_quality,
        )
        for file in uploads
    ]
    return tuple(
        UploadedImage(
            content=image.content,
            content_type=image.content_type,
            extension=image.extension,
        )
        for image in prepared
    )


def _to_response(view: ReviewView) -> ReviewResponse:
    return ReviewResponse(
        review_id=view.review_id,
        exhibit_id=view.exhibit_id,
        content=view.content,
        visit_date=view.visit_date,
        status=view.status,
        rejection_reason=view.rejection_reason,
        images=[
            ReviewImageResponse(review_image_id=image.image_id, image_url=image.url)
            for image in view.images
        ],
        created_at=view.created_at,
        updated_at=view.updated_at,
    )


def _to_image_responses(
    images: tuple[ReviewImageView, ...],
) -> list[ReviewImageResponse]:
    return [
        ReviewImageResponse(review_image_id=image.image_id, image_url=image.url)
        for image in images
    ]


def _to_exhibit_review_response(item: ExhibitReviewItem) -> ExhibitReviewResponse:
    return ExhibitReviewResponse(
        review_id=item.review_id,
        reviewer_nickname=item.reviewer_nickname,
        content=item.content,
        visit_date=item.visit_date,
        images=_to_image_responses(item.images),
        created_at=item.created_at,
    )


def _to_my_review_response(item: MyReviewItem) -> MyReviewResponse:
    return MyReviewResponse(
        review_id=item.review_id,
        exhibit_id=item.exhibit_id,
        exhibit_title=item.exhibit_title,
        poster_url=item.poster_url,
        content=item.content,
        visit_date=item.visit_date,
        status=item.status,
        rejection_reason=item.rejection_reason,
        images=_to_image_responses(item.images),
        created_at=item.created_at,
    )
