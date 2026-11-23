from typing import Final

from psycopg.errors import UniqueViolation
from sqlalchemy import exists, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from arttrip.application.domain.review.review import Review
from arttrip.application.domain.review.review_status import ReviewStatus
from arttrip.application.port.output.review_port import (
    AuthoredReview,
    ReviewPort,
    WrittenReview,
)
from arttrip.outbound.persistence.integrity import translate_integrity_errors
from arttrip.outbound.persistence.models import exhibit_table, review_table, users_table

ONE_REVIEW_PER_EXHIBIT: Final = "uq_review_user_id_exhibit_id"


class ReviewAdapter(ReviewPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, review: Review) -> None:
        self._session.add(review)
        with translate_integrity_errors():
            self._session.flush()

    def find_by_id(self, review_id: int) -> Review | None:
        return self._session.get(Review, review_id)

    def exists_by_user_and_exhibit(self, *, user_id: int, exhibit_id: int) -> bool:
        statement = select(
            exists().where(
                review_table.c.user_id == user_id,
                review_table.c.exhibit_id == exhibit_id,
            )
        )
        return bool(self._session.scalar(statement))

    def remove(self, review: Review) -> None:
        self._session.delete(review)

    def list_approved_page(
        self, *, exhibit_id: int, cursor: int | None, limit: int
    ) -> list[AuthoredReview]:
        statement = (
            select(Review, users_table.c.nickname)
            .join(users_table, users_table.c.id == review_table.c.user_id)
            .where(
                review_table.c.exhibit_id == exhibit_id,
                review_table.c.status == ReviewStatus.APPROVED,
            )
            .order_by(review_table.c.id.desc())
            .limit(limit)
        )
        if cursor is not None:
            statement = statement.where(review_table.c.id < cursor)
        rows = self._session.execute(statement).all()
        return [
            AuthoredReview(review=review, author_nickname=nickname)
            for review, nickname in rows
        ]

    def count_approved(self, *, exhibit_id: int) -> int:
        statement = (
            select(func.count())
            .select_from(review_table)
            .where(
                review_table.c.exhibit_id == exhibit_id,
                review_table.c.status == ReviewStatus.APPROVED,
            )
        )
        return self._session.scalar(statement) or 0

    def list_page_by_user(
        self, *, user_id: int, cursor: int | None, limit: int
    ) -> list[WrittenReview]:
        statement = (
            select(Review, exhibit_table.c.title, exhibit_table.c.poster_url)
            .join(exhibit_table, exhibit_table.c.id == review_table.c.exhibit_id)
            .where(review_table.c.user_id == user_id)
            .order_by(review_table.c.id.desc())
            .limit(limit)
        )
        if cursor is not None:
            statement = statement.where(review_table.c.id < cursor)
        rows = self._session.execute(statement).all()
        return [
            WrittenReview(review=review, exhibit_title=title, poster_url=poster_url)
            for review, title, poster_url in rows
        ]

    def count_by_user(self, *, user_id: int) -> int:
        statement = (
            select(func.count())
            .select_from(review_table)
            .where(review_table.c.user_id == user_id)
        )
        return self._session.scalar(statement) or 0


def _violates(error: IntegrityError, constraint_name: str) -> bool:
    cause = error.orig
    return (
        isinstance(cause, UniqueViolation)
        and cause.diag.constraint_name == constraint_name
    )
