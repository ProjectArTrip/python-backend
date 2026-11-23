from fastapi import Request

from arttrip.application.domain.review.review_services import (
    DeleteReviewService,
    ListExhibitReviewsService,
    ListMyReviewsService,
    ReviseReviewService,
    WriteReviewService,
)
from arttrip.application.port.input.review.use_cases import (
    DeleteReviewUseCase,
    ListExhibitReviewsUseCase,
    ListMyReviewsUseCase,
    ReviseReviewUseCase,
    WriteReviewUseCase,
)
from arttrip.bootstrap.wiring.common import Overrides, new_unit_of_work
from arttrip.inbound.http.dependencies.review import (
    provide_delete_review_use_case,
    provide_list_exhibit_reviews_use_case,
    provide_list_my_reviews_use_case,
    provide_revise_review_use_case,
    provide_write_review_use_case,
)


def build_write_review_use_case(request: Request) -> WriteReviewUseCase:
    return WriteReviewService(
        uow=new_unit_of_work(request), storage=request.app.state.image_storage
    )


def build_revise_review_use_case(request: Request) -> ReviseReviewUseCase:
    return ReviseReviewService(
        uow=new_unit_of_work(request), storage=request.app.state.image_storage
    )


def build_delete_review_use_case(request: Request) -> DeleteReviewUseCase:
    return DeleteReviewService(
        uow=new_unit_of_work(request), storage=request.app.state.image_storage
    )


def build_list_exhibit_reviews_use_case(request: Request) -> ListExhibitReviewsUseCase:
    return ListExhibitReviewsService(
        uow=new_unit_of_work(request), storage=request.app.state.image_storage
    )


def build_list_my_reviews_use_case(request: Request) -> ListMyReviewsUseCase:
    return ListMyReviewsService(
        uow=new_unit_of_work(request), storage=request.app.state.image_storage
    )


def wire_review(overrides: Overrides) -> None:
    overrides[provide_write_review_use_case] = build_write_review_use_case
    overrides[provide_revise_review_use_case] = build_revise_review_use_case
    overrides[provide_delete_review_use_case] = build_delete_review_use_case
    overrides[provide_list_exhibit_reviews_use_case] = (
        build_list_exhibit_reviews_use_case
    )
    overrides[provide_list_my_reviews_use_case] = build_list_my_reviews_use_case
