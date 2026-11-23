from datetime import date

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import Session

from arttrip.application.domain.curation.curation import Curation
from arttrip.application.domain.exhibit.exhibit import Exhibit
from arttrip.application.domain.exhibit.exhibit_filter import ExhibitFilter
from arttrip.application.port.output.curation_port import (
    CuratedExhibit,
    CurationPort,
    CurationSearchRow,
)
from arttrip.outbound.persistence.exhibit_conditions import (
    build_exhibit_conditions,
    build_not_finished_condition,
)
from arttrip.outbound.persistence.models import (
    curation_exhibit_table,
    curation_table,
    exhibit_table,
)


class CurationAdapter(CurationPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, curation_id: int) -> Curation | None:
        return self._session.get(Curation, curation_id)

    def list_exhibits_page(
        self, *, curation_id: int, cursor: int | None, limit: int, today: date
    ) -> list[CuratedExhibit]:
        statement = (
            select(Exhibit, curation_exhibit_table.c.display_order)
            .join(
                curation_exhibit_table,
                curation_exhibit_table.c.exhibit_id == exhibit_table.c.id,
            )
            .where(
                curation_exhibit_table.c.curation_id == curation_id,
                build_not_finished_condition(today),
            )
            .order_by(curation_exhibit_table.c.display_order.asc())
            .limit(limit)
        )
        if cursor is not None:
            statement = statement.where(curation_exhibit_table.c.display_order > cursor)
        rows = self._session.execute(statement).all()
        return [
            CuratedExhibit(exhibit=exhibit, display_order=display_order)
            for exhibit, display_order in rows
        ]

    def list_visible_ids(self, *, today: date, criteria: ExhibitFilter) -> list[int]:
        statement = (
            select(curation_table.c.id)
            .join(
                curation_exhibit_table,
                curation_exhibit_table.c.curation_id == curation_table.c.id,
            )
            .join(
                exhibit_table,
                exhibit_table.c.id == curation_exhibit_table.c.exhibit_id,
            )
            .where(
                curation_table.c.active.is_(True),
                build_not_finished_condition(today),
                *build_exhibit_conditions(criteria),
            )
            .distinct()
        )
        return list(self._session.scalars(statement).all())

    def list_matching_exhibits(
        self, *, curation_id: int, criteria: ExhibitFilter, limit: int, today: date
    ) -> list[Exhibit]:
        statement = (
            select(Exhibit)
            .join(
                curation_exhibit_table,
                curation_exhibit_table.c.exhibit_id == exhibit_table.c.id,
            )
            .where(
                curation_exhibit_table.c.curation_id == curation_id,
                build_not_finished_condition(today),
                *build_exhibit_conditions(criteria),
            )
            .order_by(curation_exhibit_table.c.display_order.asc())
            .limit(limit)
        )
        return list(self._session.scalars(statement).all())

    def search_page(
        self, *, keyword: str | None, active: bool | None, offset: int, limit: int
    ) -> list[CurationSearchRow]:
        exhibit_count = (
            select(func.count(curation_exhibit_table.c.id))
            .where(curation_exhibit_table.c.curation_id == curation_table.c.id)
            .scalar_subquery()
        )
        statement = (
            select(Curation, curation_table.c.created_at, exhibit_count)
            .where(*_search_conditions(keyword, active))
            .order_by(curation_table.c.created_at.desc(), curation_table.c.id.desc())
            .offset(offset)
            .limit(limit)
        )
        rows = self._session.execute(statement).all()
        return [
            CurationSearchRow(
                curation=curation, exhibit_count=count, created_at=created_at
            )
            for curation, created_at, count in rows
        ]

    def count_search(self, *, keyword: str | None, active: bool | None) -> int:
        statement = (
            select(func.count())
            .select_from(curation_table)
            .where(*_search_conditions(keyword, active))
        )
        return self._session.scalar(statement) or 0

    def list_exhibits(self, curation_id: int) -> list[Exhibit]:
        statement = (
            select(Exhibit)
            .join(
                curation_exhibit_table,
                curation_exhibit_table.c.exhibit_id == exhibit_table.c.id,
            )
            .where(curation_exhibit_table.c.curation_id == curation_id)
            .order_by(curation_exhibit_table.c.display_order.asc())
        )
        return list(self._session.scalars(statement).all())

    def add(self, curation: Curation) -> None:
        self._session.add(curation)
        self._session.flush()

    def remove(self, curation: Curation) -> None:
        self._session.delete(curation)


def _search_conditions(
    keyword: str | None, active: bool | None
) -> list[ColumnElement[bool]]:
    conditions: list[ColumnElement[bool]] = []
    if keyword is not None:
        conditions.append(curation_table.c.title.icontains(keyword, autoescape=True))
    if active is not None:
        conditions.append(curation_table.c.active.is_(active))
    return conditions
