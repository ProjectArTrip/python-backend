from datetime import date

from sqlalchemy import ColumnElement, Select, exists, or_, select

from arttrip.application.domain.exhibit.exhibit_filter import ExhibitFilter
from arttrip.application.domain.exhibit.exhibit_hall import DEFAULT_COUNTRY_CODE
from arttrip.outbound.persistence.models import (
    country_alias_table,
    country_table,
    exhibit_hall_table,
    exhibit_keyword_table,
    exhibit_table,
    keyword_table,
)


def build_exhibit_conditions(criteria: ExhibitFilter) -> list[ColumnElement[bool]]:
    conditions: list[ColumnElement[bool]] = []

    if criteria.period_end is not None:
        conditions.append(exhibit_table.c.start_date <= criteria.period_end)
    if criteria.period_start is not None:
        conditions.append(exhibit_table.c.end_date >= criteria.period_start)

    hall_conditions: list[ColumnElement[bool]] = []
    if criteria.domestic is True:
        hall_conditions.append(
            exhibit_hall_table.c.country_code == DEFAULT_COUNTRY_CODE
        )
    if criteria.domestic is False:
        hall_conditions.append(
            exhibit_hall_table.c.country_code != DEFAULT_COUNTRY_CODE
        )
    if criteria.country_code is not None:
        hall_conditions.append(
            exhibit_hall_table.c.country_code == criteria.country_code
        )
    if criteria.regions:
        hall_conditions.append(exhibit_hall_table.c.region.in_(criteria.regions))
    if hall_conditions:
        conditions.append(_hall_matches(*hall_conditions))

    for keyword_ids in (criteria.genre_ids, criteria.style_ids):
        if keyword_ids:
            conditions.append(
                has_keyword(exhibit_keyword_table.c.keyword_id.in_(keyword_ids))
            )

    if criteria.search_text is not None:
        text = criteria.search_text
        conditions.append(
            or_(
                exhibit_table.c.title.icontains(text, autoescape=True),
                _hall_matches(
                    or_(
                        exhibit_hall_table.c.name.icontains(text, autoescape=True),
                        exhibit_hall_table.c.region.icontains(text, autoescape=True),
                        exhibit_hall_table.c.country_code.in_(
                            _country_codes_named_like(text)
                        ),
                    )
                ),
                has_keyword(
                    exhibit_keyword_table.c.keyword_id.in_(
                        select(keyword_table.c.id).where(
                            keyword_table.c.name.icontains(text, autoescape=True)
                        )
                    )
                ),
            )
        )
    return conditions


def build_not_finished_condition(today: date) -> ColumnElement[bool]:
    return or_(
        exhibit_table.c.end_date.is_(None),
        exhibit_table.c.end_date >= today,
    )


def _hall_matches(*hall_conditions: ColumnElement[bool]) -> ColumnElement[bool]:
    return exists().where(
        exhibit_hall_table.c.id == exhibit_table.c.exhibit_hall_id, *hall_conditions
    )


def has_keyword(keyword_condition: ColumnElement[bool]) -> ColumnElement[bool]:
    return exists().where(
        exhibit_keyword_table.c.exhibit_id == exhibit_table.c.id, keyword_condition
    )


def _country_codes_named_like(text: str) -> Select[tuple[str]]:
    alias_matches = exists().where(
        country_alias_table.c.country_id == country_table.c.id,
        country_alias_table.c.name.icontains(text, autoescape=True),
    )
    return select(country_table.c.code).where(
        or_(country_table.c.name.icontains(text, autoescape=True), alias_matches)
    )
