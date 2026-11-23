from typing import Annotated

from fastapi import Depends

from arttrip.application.port.input.review.use_cases import (
    DeleteReviewUseCase,
    ListExhibitReviewsUseCase,
    ListMyReviewsUseCase,
    ReviseReviewUseCase,
    WriteReviewUseCase,
)


def provide_write_review_use_case() -> WriteReviewUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_revise_review_use_case() -> ReviseReviewUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_delete_review_use_case() -> DeleteReviewUseCase:
    raise NotImplementedError("composition root must override this dependency")


WriteReviewUseCaseDep = Annotated[
    WriteReviewUseCase, Depends(provide_write_review_use_case)
]
ReviseReviewUseCaseDep = Annotated[
    ReviseReviewUseCase, Depends(provide_revise_review_use_case)
]
DeleteReviewUseCaseDep = Annotated[
    DeleteReviewUseCase, Depends(provide_delete_review_use_case)
]


def provide_list_exhibit_reviews_use_case() -> ListExhibitReviewsUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_list_my_reviews_use_case() -> ListMyReviewsUseCase:
    raise NotImplementedError("composition root must override this dependency")


ListExhibitReviewsUseCaseDep = Annotated[
    ListExhibitReviewsUseCase, Depends(provide_list_exhibit_reviews_use_case)
]
ListMyReviewsUseCaseDep = Annotated[
    ListMyReviewsUseCase, Depends(provide_list_my_reviews_use_case)
]
