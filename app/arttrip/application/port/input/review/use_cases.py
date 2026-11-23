from abc import ABC, abstractmethod

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
    ListExhibitReviewsResult,
    ListMyReviewsResult,
    ReviewView,
)


class WriteReviewUseCase(ABC):
    @abstractmethod
    def write_review(self, command: WriteReviewCommand) -> ReviewView:
        pass


class ReviseReviewUseCase(ABC):
    @abstractmethod
    def revise_review(self, command: ReviseReviewCommand) -> ReviewView:
        pass


class DeleteReviewUseCase(ABC):
    @abstractmethod
    def delete_review(self, command: DeleteReviewCommand) -> None:
        pass


class ListExhibitReviewsUseCase(ABC):
    @abstractmethod
    def list_exhibit_reviews(
        self, query: ListExhibitReviewsQuery
    ) -> ListExhibitReviewsResult:
        pass


class ListMyReviewsUseCase(ABC):
    @abstractmethod
    def list_my_reviews(self, query: ListMyReviewsQuery) -> ListMyReviewsResult:
        pass
