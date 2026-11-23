from datetime import date

from arttrip.application.domain.exhibit.country import Country
from arttrip.application.domain.exhibit.exceptions import ExhibitError
from arttrip.application.domain.exhibit.exhibit import Exhibit
from arttrip.application.domain.exhibit.exhibit_hall import (
    DEFAULT_COUNTRY_CODE,
    ExhibitHall,
)
from arttrip.application.domain.exhibit.exhibit_status_policy import ExhibitStatusPolicy
from arttrip.application.domain.keyword.keyword import Keyword
from arttrip.application.domain.keyword.keyword_type import KeywordType
from arttrip.application.port.input.exhibit.commands import (
    CreateExhibitCommand,
)
from arttrip.application.port.output.unit_of_work import UnitOfWork


def new_hall(command: CreateExhibitCommand, *, country_code: str) -> ExhibitHall:
    return ExhibitHall.create(
        name=command.hall_name.strip(),
        country_code=country_code,
        region=command.region,
        address=command.address,
        opening_hours=command.opening_hours,
        phone=command.phone,
        latitude=command.latitude,
        longitude=command.longitude,
    )


def new_exhibit(
    command: CreateExhibitCommand,
    *,
    hall: ExhibitHall,
    today: date,
    policy: ExhibitStatusPolicy,
    owner_id: int | None = None,
) -> Exhibit:
    return Exhibit.create(
        hall=hall,
        title=command.title.strip(),
        description=command.description,
        poster_url=command.poster_url,
        ticket_url=command.ticket_url,
        start_date=command.start_date,
        end_date=command.end_date,
        today=today,
        policy=policy,
        owner_id=owner_id,
    )


def revise_hall(
    hall: ExhibitHall, command: CreateExhibitCommand, *, country_code: str
) -> None:
    hall.revise(
        name=command.hall_name.strip(),
        country_code=country_code,
        region=command.region,
        address=command.address,
        opening_hours=command.opening_hours,
        phone=command.phone,
        latitude=command.latitude,
        longitude=command.longitude,
    )


def find_keywords(
    uow: UnitOfWork, keyword_type: KeywordType, names: frozenset[str]
) -> list[Keyword]:
    if not names:
        return []
    found = uow.keywords.find_by_names(keyword_type=keyword_type, names=names)
    wanted = {Keyword.normalize_name(name) for name in names}
    if {keyword.normalized_name for keyword in found} != wanted:
        raise ExhibitError.unknown_keyword()
    return found


def resolve_country(uow: UnitOfWork, *, name: str, is_domestic: bool | None) -> Country:
    if is_domestic:
        country = uow.locations.find_country_by_code(DEFAULT_COUNTRY_CODE)
    else:
        country = uow.locations.find_country_by_name(name)
    if country is None:
        raise ExhibitError.unknown_country()
    if is_domestic is False:
        country.ensure_overseas()
    return country
