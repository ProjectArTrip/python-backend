from collections.abc import Callable, Collection
from dataclasses import dataclass
from datetime import date
from typing import Any, Final

from sqlalchemy import ColumnElement, FromClause, and_, case, delete, func, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from arttrip.application.domain.exhibit.exhibit import Exhibit
from arttrip.application.domain.exhibit.exhibit_filter import ExhibitFilter
from arttrip.application.domain.favorite.favorite import Favorite
from arttrip.application.domain.favorite.favorite_sort import FavoriteSort
from arttrip.application.port.output.favorite_port import FavoritedExhibit, FavoritePort
from arttrip.outbound.persistence.exhibit_conditions import build_exhibit_conditions
from arttrip.outbound.persistence.models import exhibit_table, favorite_table


@dataclass(frozen=True)
class _SortPlan:
    order_by: tuple[ColumnElement[Any], ...]
    cursor_column: ColumnElement[int]
    is_after: Callable[[int], ColumnElement[bool]]


def _plan_latest(today: date) -> _SortPlan:
    return _SortPlan(
        order_by=(favorite_table.c.id.desc(),),
        cursor_column=favorite_table.c.id,
        is_after=lambda cursor: favorite_table.c.id < cursor,
    )


def _ending_soon_key(exhibits: FromClause, today: date) -> ColumnElement[date]:
    return case(
        (exhibits.c.end_date >= today, exhibits.c.end_date),
        else_=date.max,
    )


def _plan_ending_soon(today: date) -> _SortPlan:
    sort_key = _ending_soon_key(exhibit_table, today)

    def is_after(cursor: int) -> ColumnElement[bool]:
        cursor_exhibit = exhibit_table.alias("cursor_exhibit")
        cursor_key = (
            select(_ending_soon_key(cursor_exhibit, today))
            .where(cursor_exhibit.c.id == cursor)
            .scalar_subquery()
        )
        return or_(
            sort_key > cursor_key,
            and_(sort_key == cursor_key, exhibit_table.c.id > cursor),
        )

    return _SortPlan(
        order_by=(sort_key.asc(), exhibit_table.c.id.asc()),
        cursor_column=exhibit_table.c.id,
        is_after=is_after,
    )


_SORT_PLANS: Final[dict[FavoriteSort, Callable[[date], _SortPlan]]] = {
    FavoriteSort.LATEST: _plan_latest,
    FavoriteSort.ENDING_SOON: _plan_ending_soon,
}


class FavoriteAdapter(FavoritePort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, favorite: Favorite) -> None:
        statement = (
            insert(favorite_table)
            .values(
                user_id=favorite.user_id,
                exhibit_id=favorite.exhibit_id,
                created_at=favorite.created_at,
            )
            .on_conflict_do_nothing(
                index_elements=[favorite_table.c.user_id, favorite_table.c.exhibit_id]
            )
        )
        self._session.execute(statement)

    def remove(self, *, user_id: int, exhibit_id: int) -> None:
        statement = delete(favorite_table).where(
            favorite_table.c.user_id == user_id,
            favorite_table.c.exhibit_id == exhibit_id,
        )
        self._session.execute(statement)

    def list_page(
        self,
        *,
        user_id: int,
        criteria: ExhibitFilter,
        sort: FavoriteSort,
        cursor: int | None,
        today: date,
        limit: int,
    ) -> list[FavoritedExhibit]:
        plan = _SORT_PLANS[sort](today)
        statement = (
            select(Exhibit, plan.cursor_column.label("cursor"))
            .join(favorite_table, favorite_table.c.exhibit_id == exhibit_table.c.id)
            .where(
                favorite_table.c.user_id == user_id,
                *build_exhibit_conditions(criteria),
            )
            .order_by(*plan.order_by)
            .limit(limit)
        )
        if cursor is not None:
            statement = statement.where(plan.is_after(cursor))
        rows = self._session.execute(statement).all()
        return [
            FavoritedExhibit(exhibit=exhibit, cursor=row_cursor)
            for exhibit, row_cursor in rows
        ]

    def count(self, *, user_id: int, criteria: ExhibitFilter) -> int:
        favorite_with_exhibit = favorite_table.join(
            exhibit_table, exhibit_table.c.id == favorite_table.c.exhibit_id
        )
        statement = (
            select(func.count())
            .select_from(favorite_with_exhibit)
            .where(
                favorite_table.c.user_id == user_id,
                *build_exhibit_conditions(criteria),
            )
        )
        return self._session.scalar(statement) or 0

    def find_exhibit_ids(
        self, *, user_id: int, exhibit_ids: Collection[int]
    ) -> set[int]:
        if not exhibit_ids:
            return set()
        statement = select(favorite_table.c.exhibit_id).where(
            favorite_table.c.user_id == user_id,
            favorite_table.c.exhibit_id.in_(exhibit_ids),
        )
        return set(self._session.scalars(statement).all())
