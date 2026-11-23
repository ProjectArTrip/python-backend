from collections.abc import Collection, Sequence
from datetime import date
from typing import Any, Final

from sqlalchemy import (
    ColumnElement,
    case,
    delete,
    exists,
    func,
    literal,
    select,
    tuple_,
    update,
)
from sqlalchemy.orm import Session

from arttrip.application.domain.exhibit.exhibit import Exhibit
from arttrip.application.domain.exhibit.exhibit_filter import ExhibitFilter
from arttrip.application.domain.exhibit.exhibit_hall import (
    ExhibitHall,
)
from arttrip.application.domain.exhibit.exhibit_list_sort import (
    ExhibitListCursor,
    ExhibitListSort,
)
from arttrip.application.domain.exhibit.exhibit_search import (
    ExhibitSearch,
    ExhibitSortField,
)
from arttrip.application.domain.exhibit.exhibit_status import ExhibitStatus
from arttrip.application.domain.exhibit.exhibit_status_policy import ExhibitStatusPolicy
from arttrip.application.domain.keyword.keyword_type import KeywordType
from arttrip.application.port.output.exhibit_port import ExhibitKey, ExhibitPort
from arttrip.application.util.sort_direction import SortDirection
from arttrip.outbound.persistence.exhibit_conditions import (
    build_exhibit_conditions,
    build_not_finished_condition,
    has_keyword,
)
from arttrip.outbound.persistence.integrity import (
    translate_integrity_errors,
)
from arttrip.outbound.persistence.models import (
    curation_exhibit_table,
    exhibit_hall_table,
    exhibit_keyword_table,
    exhibit_sync_table,
    exhibit_table,
    favorite_table,
    keyword_table,
    recent_exhibit_table,
    review_image_table,
    review_table,
)

_SORT_COLUMNS: Final[dict[ExhibitSortField, ColumnElement[Any]]] = {
    ExhibitSortField.CREATED_AT: exhibit_table.c.created_at,
    ExhibitSortField.START_DATE: exhibit_table.c.start_date,
    ExhibitSortField.END_DATE: exhibit_table.c.end_date,
    ExhibitSortField.TITLE: exhibit_table.c.title,
}


class ExhibitAdapter(ExhibitPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, exhibit_id: int) -> Exhibit | None:
        return self._session.get(Exhibit, exhibit_id)

    def increment_view_count(self, exhibit_id: int) -> None:
        self._session.execute(
            update(exhibit_table)
            .where(exhibit_table.c.id == exhibit_id)
            .values(view_count=exhibit_table.c.view_count + 1)
        )

    def list_page(
        self,
        *,
        criteria: ExhibitFilter,
        sort: ExhibitListSort,
        cursor: ExhibitListCursor | None,
        limit: int,
    ) -> list[tuple[Exhibit, ExhibitListCursor]]:
        sort_key = _list_sort_key(sort)
        ascending = sort is ExhibitListSort.ENDING_SOON
        order = (
            (sort_key.asc(), exhibit_table.c.id.asc())
            if ascending
            else (
                sort_key.desc(),
                exhibit_table.c.id.desc(),
            )
        )
        statement = (
            select(Exhibit, sort_key)
            .where(*build_exhibit_conditions(criteria))
            .order_by(*order)
            .limit(limit)
        )
        if cursor is not None:
            current = tuple_(sort_key, exhibit_table.c.id)
            boundary = tuple_(literal(cursor.value), literal(cursor.exhibit_id))
            statement = statement.where(
                current > boundary if ascending else current < boundary
            )
        return [
            (exhibit, ExhibitListCursor(sort=sort, value=value, exhibit_id=exhibit.id))
            for exhibit, value in self._session.execute(statement).all()
            if exhibit.id is not None
        ]

    def search_page(
        self,
        *,
        search: ExhibitSearch,
        today: date,
        policy: ExhibitStatusPolicy,
        sort: ExhibitSortField,
        direction: SortDirection,
        offset: int,
        limit: int,
    ) -> list[Exhibit]:
        column = _SORT_COLUMNS[sort]
        ordered = column.asc() if direction is SortDirection.ASC else column.desc()
        statement = (
            select(Exhibit)
            .where(*_build_search_conditions(search, today, policy))
            .order_by(ordered.nulls_last(), exhibit_table.c.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self._session.scalars(statement).all())

    def count_search(
        self, *, search: ExhibitSearch, today: date, policy: ExhibitStatusPolicy
    ) -> int:
        statement = (
            select(func.count())
            .select_from(exhibit_table)
            .where(*_build_search_conditions(search, today, policy))
        )
        return self._session.scalar(statement) or 0

    def find_ids_by_owner(self, owner_id: int) -> list[int]:
        statement = select(exhibit_table.c.id).where(
            exhibit_table.c.owner_user_id == owner_id
        )
        return list(self._session.scalars(statement).all())

    def remove_with_dependents(self, exhibit_id: int) -> None:
        exhibit_reviews = select(review_table.c.id).where(
            review_table.c.exhibit_id == exhibit_id
        )
        self._session.execute(
            delete(review_image_table).where(
                review_image_table.c.review_id.in_(exhibit_reviews)
            )
        )
        dependent_tables = (
            review_table,
            curation_exhibit_table,
            recent_exhibit_table,
            favorite_table,
            exhibit_sync_table,
            exhibit_keyword_table,
        )
        for table in dependent_tables:
            self._session.execute(delete(table).where(table.c.exhibit_id == exhibit_id))
        self._session.execute(
            delete(exhibit_table).where(exhibit_table.c.id == exhibit_id)
        )

    def find_by_ids(self, exhibit_ids: Sequence[int]) -> list[Exhibit]:
        if not exhibit_ids:
            return []
        statement = select(Exhibit).where(exhibit_table.c.id.in_(exhibit_ids))
        found = {exhibit.id: exhibit for exhibit in self._session.scalars(statement)}
        return [found[exhibit_id] for exhibit_id in exhibit_ids if exhibit_id in found]

    def find_existing_ids(self, exhibit_ids: Collection[int]) -> set[int]:
        statement = select(exhibit_table.c.id).where(
            exhibit_table.c.id.in_(exhibit_ids)
        )
        return set(self._session.scalars(statement).all())

    def find_existing_keys(self, keys: Collection[ExhibitKey]) -> set[ExhibitKey]:
        hall_names = {hall_name for hall_name, _, _ in keys}
        if not hall_names:
            return set()
        statement = (
            select(
                exhibit_hall_table.c.name,
                exhibit_table.c.title,
                exhibit_table.c.start_date,
            )
            .join(
                exhibit_hall_table,
                exhibit_hall_table.c.id == exhibit_table.c.exhibit_hall_id,
            )
            .where(exhibit_hall_table.c.name.in_(hall_names))
        )
        found: set[ExhibitKey] = set()
        for hall_name, title, start_date in self._session.execute(statement):
            key = (hall_name, title, start_date)
            if title is not None and key in keys:
                found.add(key)
        return found

    def add(self, exhibit: Exhibit) -> None:
        self._session.add(exhibit)
        with translate_integrity_errors():
            self._session.flush()

    def find_hall_by_name(self, name: str) -> ExhibitHall | None:
        statement = (
            select(ExhibitHall)
            .where(exhibit_hall_table.c.name == name)
            .order_by(exhibit_hall_table.c.id)
        )
        return self._session.scalars(statement).first()

    def find_halls_by_names(self, names: Collection[str]) -> list[ExhibitHall]:
        if not names:
            return []
        statement = (
            select(ExhibitHall)
            .where(exhibit_hall_table.c.name.in_(names))
            .order_by(exhibit_hall_table.c.id)
        )
        return list(self._session.scalars(statement).all())

    def add_all(self, exhibits: Sequence[Exhibit]) -> None:
        self._session.add_all(exhibits)
        with translate_integrity_errors():
            self._session.flush()

    def exists_same(self, *, hall_id: int, title: str, start_date: date | None) -> bool:
        same_start = (
            exhibit_table.c.start_date.is_(None)
            if start_date is None
            else exhibit_table.c.start_date == start_date
        )
        statement = select(
            exists().where(
                exhibit_table.c.exhibit_hall_id == hall_id,
                exhibit_table.c.title == title,
                same_start,
            )
        )
        return bool(self._session.scalar(statement))

    def pick_random(
        self, *, criteria: ExhibitFilter, today: date, pivot: float, limit: int
    ) -> list[Exhibit]:
        conditions = [
            build_not_finished_condition(today),
            *build_exhibit_conditions(criteria),
        ]
        picked = self._fetch_ordered_by_random_key(
            conditions, exhibit_table.c.random_key >= pivot, limit
        )
        if len(picked) < limit:
            picked += self._fetch_ordered_by_random_key(
                conditions, exhibit_table.c.random_key < pivot, limit - len(picked)
            )
        return picked

    def _fetch_ordered_by_random_key(
        self,
        conditions: list[ColumnElement[bool]],
        random_condition: ColumnElement[bool],
        limit: int,
    ) -> list[Exhibit]:
        statement = (
            select(Exhibit)
            .where(*conditions, random_condition)
            .order_by(exhibit_table.c.random_key.asc())
            .limit(limit)
        )
        return list(self._session.scalars(statement).all())


def _build_search_conditions(
    search: ExhibitSearch, today: date, policy: ExhibitStatusPolicy
) -> list[ColumnElement[bool]]:
    conditions = build_exhibit_conditions(search.criteria)
    if search.statuses:
        conditions.append(
            _status_expression(today, policy).in_(
                [status.value for status in search.statuses]
            )
        )
    if search.genre_names:
        conditions.append(
            has_keyword(
                exhibit_keyword_table.c.keyword_id.in_(
                    select(keyword_table.c.id).where(
                        keyword_table.c.type == KeywordType.GENRE,
                        keyword_table.c.name.in_(search.genre_names),
                    )
                )
            )
        )
    if search.owner_id is not None:
        conditions.append(exhibit_table.c.owner_user_id == search.owner_id)
    return conditions


def _status_expression(today: date, policy: ExhibitStatusPolicy) -> ColumnElement[str]:
    return case(
        (exhibit_table.c.start_date > today, ExhibitStatus.UPCOMING.value),
        (exhibit_table.c.end_date.is_(None), ExhibitStatus.ONGOING.value),
        (exhibit_table.c.end_date < today, ExhibitStatus.FINISHED.value),
        (
            exhibit_table.c.end_date <= policy.ending_soon_until(today),
            ExhibitStatus.ENDING_SOON.value,
        ),
        else_=ExhibitStatus.ONGOING.value,
    )


def _list_sort_key(sort: ExhibitListSort) -> ColumnElement[Any]:
    if sort is ExhibitListSort.POPULAR:
        favorite_count = (
            select(func.count())
            .where(favorite_table.c.exhibit_id == exhibit_table.c.id)
            .scalar_subquery()
        )
        return exhibit_table.c.view_count + favorite_count
    if sort is ExhibitListSort.ENDING_SOON:
        return func.coalesce(exhibit_table.c.end_date, date.max)
    return exhibit_table.c.id
