from abc import ABC, abstractmethod
from dataclasses import dataclass

from arttrip.application.domain.review.review import Review


class ReviewPort(ABC):
    @abstractmethod
    def add(self, review: Review) -> None:
        pass

    @abstractmethod
    def find_by_id(self, review_id: int) -> Review | None:
        pass

    @abstractmethod
    def exists_by_user_and_exhibit(self, *, user_id: int, exhibit_id: int) -> bool:
        pass

    @abstractmethod
    def remove(self, review: Review) -> None:
        pass

    @abstractmethod
    def list_approved_page(
        self, *, exhibit_id: int, cursor: int | None, limit: int
    ) -> list[AuthoredReview]:
        pass

    @abstractmethod
    def count_approved(self, *, exhibit_id: int) -> int:
        pass

    @abstractmethod
    def list_page_by_user(
        self, *, user_id: int, cursor: int | None, limit: int
    ) -> list[WrittenReview]:
        pass

    @abstractmethod
    def count_by_user(self, *, user_id: int) -> int:
        pass


@dataclass(frozen=True)
class AuthoredReview:
    review: Review
    author_nickname: str


@dataclass(frozen=True)
class WrittenReview:
    review: Review
    exhibit_title: str | None
    poster_url: str | None
