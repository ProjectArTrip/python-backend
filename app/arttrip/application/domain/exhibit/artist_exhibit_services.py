from datetime import UTC, datetime

from arttrip.application.domain.exhibit.exceptions import ExhibitError
from arttrip.application.domain.exhibit.exhibit_factory import (
    find_keywords,
    new_exhibit,
    new_hall,
    resolve_country,
)
from arttrip.application.domain.exhibit.exhibit_filter import ExhibitFilter
from arttrip.application.domain.exhibit.exhibit_management_services import (
    search_exhibit_page,
)
from arttrip.application.domain.exhibit.exhibit_search import (
    ExhibitSearch,
    ExhibitSortField,
)
from arttrip.application.domain.exhibit.exhibit_status_policy import ExhibitStatusPolicy
from arttrip.application.domain.keyword.keyword_type import KeywordType
from arttrip.application.domain.user.current_user import load_current_user
from arttrip.application.port.input.exhibit.commands import (
    DeleteArtistExhibitCommand,
    RegisterArtistExhibitCommand,
    UpdateArtistExhibitCommand,
)
from arttrip.application.port.input.exhibit.queries import (
    ListArtistExhibitsQuery,
    SearchExhibitsQuery,
)
from arttrip.application.port.input.exhibit.results import ExhibitSearchItem
from arttrip.application.port.input.exhibit.use_cases import (
    DeleteArtistExhibitUseCase,
    ListArtistExhibitsUseCase,
    RegisterArtistExhibitUseCase,
    UpdateArtistExhibitUseCase,
)
from arttrip.application.port.input.pagination import OffsetPage
from arttrip.application.port.output.unit_of_work import UnitOfWork
from arttrip.application.util.service_date import to_service_date
from arttrip.application.util.sort_direction import SortDirection


class RegisterArtistExhibitService(RegisterArtistExhibitUseCase):
    def __init__(self, *, uow: UnitOfWork, status_policy: ExhibitStatusPolicy) -> None:
        self._uow = uow
        self._status_policy = status_policy

    def register_artist_exhibit(self, command: RegisterArtistExhibitCommand) -> int:
        today = to_service_date(datetime.now(UTC))
        exhibit_input = command.exhibit
        title = exhibit_input.title.strip()
        hall_name = exhibit_input.hall_name.strip()

        with self._uow as uow:
            artist = load_current_user(uow.users, command.artist_id)
            artist.ensure_artist()

            country = resolve_country(
                uow,
                name=exhibit_input.country_name,
                is_domestic=exhibit_input.is_domestic,
            )
            keywords = [
                *find_keywords(uow, KeywordType.GENRE, exhibit_input.genre_names),
                *find_keywords(uow, KeywordType.STYLE, exhibit_input.style_names),
            ]
            hall = uow.exhibits.find_hall_by_name(hall_name)
            if hall is None:
                hall = new_hall(exhibit_input, country_code=country.code)
            elif hall.id is not None and uow.exhibits.exists_same(
                hall_id=hall.id, title=title, start_date=exhibit_input.start_date
            ):
                raise ExhibitError.duplicate()

            exhibit = new_exhibit(
                exhibit_input,
                hall=hall,
                today=today,
                policy=self._status_policy,
                owner_id=command.artist_id,
            )
            exhibit.replace_keywords(keywords)
            uow.exhibits.add(exhibit)
            exhibit_id = exhibit.id
        if exhibit_id is None:
            raise RuntimeError("exhibit must be persisted before returning its id")
        return exhibit_id


class ListArtistExhibitsService(ListArtistExhibitsUseCase):
    def __init__(self, *, uow: UnitOfWork, status_policy: ExhibitStatusPolicy) -> None:
        self._uow = uow
        self._status_policy = status_policy

    def list_artist_exhibits(
        self, query: ListArtistExhibitsQuery
    ) -> OffsetPage[ExhibitSearchItem]:
        today = to_service_date(datetime.now(UTC))
        with self._uow as uow:
            artist = load_current_user(uow.users, query.artist_id)
            artist.ensure_artist()
            own_exhibits = SearchExhibitsQuery(
                search=ExhibitSearch(
                    criteria=ExhibitFilter(), owner_id=query.artist_id
                ),
                country_name=None,
                sort=ExhibitSortField.CREATED_AT,
                direction=SortDirection.DESC,
                page=query.page,
                size=query.size,
            )
            return search_exhibit_page(
                uow, own_exhibits, today=today, policy=self._status_policy
            )


class UpdateArtistExhibitService(UpdateArtistExhibitUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def update_artist_exhibit(self, command: UpdateArtistExhibitCommand) -> None:
        exhibit_input = command.exhibit
        hall_name = exhibit_input.hall_name.strip()

        with self._uow as uow:
            artist = load_current_user(uow.users, command.artist_id)
            artist.ensure_artist()

            exhibit = uow.exhibits.find_by_id(command.exhibit_id)
            if exhibit is None:
                raise ExhibitError.not_found()
            exhibit.ensure_owned_by(command.artist_id)

            country = resolve_country(
                uow,
                name=exhibit_input.country_name,
                is_domestic=exhibit_input.is_domestic,
            )
            keywords = [
                *find_keywords(uow, KeywordType.GENRE, exhibit_input.genre_names),
                *find_keywords(uow, KeywordType.STYLE, exhibit_input.style_names),
            ]
            hall = uow.exhibits.find_hall_by_name(hall_name)
            if hall is None:
                hall = new_hall(exhibit_input, country_code=country.code)

            exhibit.revise(
                title=exhibit_input.title.strip(),
                description=exhibit_input.description,
                poster_url=exhibit_input.poster_url,
                ticket_url=exhibit_input.ticket_url,
                start_date=exhibit_input.start_date,
                end_date=exhibit_input.end_date,
            )
            exhibit.hall = hall
            exhibit.replace_keywords(keywords)


class DeleteArtistExhibitService(DeleteArtistExhibitUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def delete_artist_exhibit(self, command: DeleteArtistExhibitCommand) -> None:
        with self._uow as uow:
            artist = load_current_user(uow.users, command.artist_id)
            artist.ensure_artist()

            exhibit = uow.exhibits.find_by_id(command.exhibit_id)
            if exhibit is None:
                raise ExhibitError.not_found()
            exhibit.ensure_owned_by(command.artist_id)

            uow.exhibits.remove_with_dependents(command.exhibit_id)
