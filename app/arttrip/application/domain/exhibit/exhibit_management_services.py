import logging
from collections import defaultdict
from dataclasses import replace
from datetime import UTC, date, datetime

from arttrip.application.domain.exhibit.exceptions import ExhibitError
from arttrip.application.domain.exhibit.exhibit_factory import (
    find_keywords,
    new_exhibit,
    new_hall,
    resolve_country,
    revise_hall,
)
from arttrip.application.domain.exhibit.exhibit_search import (
    ExhibitSearch,
)
from arttrip.application.domain.exhibit.exhibit_status_policy import ExhibitStatusPolicy
from arttrip.application.domain.keyword.keyword_type import KeywordType
from arttrip.application.domain.notification.notification import Notification
from arttrip.application.domain.notification.notification_action import (
    NotificationAction,
)
from arttrip.application.port.input.exhibit.commands import (
    CreateExhibitCommand,
    UpdateExhibitCommand,
)
from arttrip.application.port.input.exhibit.queries import (
    SearchExhibitsQuery,
)
from arttrip.application.port.input.exhibit.results import (
    ExhibitSearchItem,
    ManagedExhibit,
)
from arttrip.application.port.input.exhibit.use_cases import (
    CreateExhibitUseCase,
    DeleteExhibitUseCase,
    GetManagedExhibitUseCase,
    SearchExhibitsUseCase,
    UpdateExhibitUseCase,
)
from arttrip.application.port.input.notification.commands import SendPushCommand
from arttrip.application.port.input.notification.use_cases import SendPushUseCase
from arttrip.application.port.input.pagination import OffsetPage
from arttrip.application.port.output.unit_of_work import UnitOfWork
from arttrip.application.util.service_date import to_service_date

_logger = logging.getLogger(__name__)


class SearchExhibitsService(SearchExhibitsUseCase):
    def __init__(self, *, uow: UnitOfWork, status_policy: ExhibitStatusPolicy) -> None:
        self._uow = uow
        self._status_policy = status_policy

    def search_exhibits(
        self, query: SearchExhibitsQuery
    ) -> OffsetPage[ExhibitSearchItem]:
        today = to_service_date(datetime.now(UTC))
        with self._uow as uow:
            return search_exhibit_page(
                uow, query, today=today, policy=self._status_policy
            )


class GetManagedExhibitService(GetManagedExhibitUseCase):
    def __init__(self, *, uow: UnitOfWork, status_policy: ExhibitStatusPolicy) -> None:
        self._uow = uow
        self._status_policy = status_policy

    def get_managed_exhibit(self, exhibit_id: int) -> ManagedExhibit:
        today = to_service_date(datetime.now(UTC))
        with self._uow as uow:
            exhibit = uow.exhibits.find_by_id(exhibit_id)

            if exhibit is None:
                raise ExhibitError.not_found()
            hall = exhibit.hall
            managed_exhibit_id = exhibit.id
            hall_id = hall.id
            if managed_exhibit_id is None or hall_id is None:
                raise ExhibitError.not_found()

            return ManagedExhibit(
                exhibit_id=managed_exhibit_id,
                title=exhibit.title,
                description=exhibit.description,
                poster_url=exhibit.poster_url,
                ticket_url=exhibit.ticket_url,
                start_date=exhibit.start_date,
                end_date=exhibit.end_date,
                status=exhibit.status_on(today=today, policy=self._status_policy),
                hall_id=hall_id,
                hall_name=hall.name,
                country_name=_country_names(uow).get(
                    hall.country_code, hall.country_code
                ),
                region=hall.region,
                address=hall.address,
                opening_hours=hall.opening_hours,
                phone=hall.phone,
                latitude=hall.latitude,
                longitude=hall.longitude,
                is_domestic=hall.is_domestic,
                genres=exhibit.keyword_names(KeywordType.GENRE),
                styles=exhibit.keyword_names(KeywordType.STYLE),
            )


class UpdateExhibitService(UpdateExhibitUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def update_exhibit(self, command: UpdateExhibitCommand) -> None:
        with self._uow as uow:
            exhibit = uow.exhibits.find_by_id(command.exhibit_id)
            if exhibit is None:
                raise ExhibitError.not_found()
            keywords = [
                *find_keywords(uow, KeywordType.GENRE, command.genre_names),
                *find_keywords(uow, KeywordType.STYLE, command.style_names),
            ]
            country = resolve_country(
                uow, name=command.country_name, is_domestic=command.is_domestic
            )
            exhibit.revise(
                title=command.title,
                description=command.description,
                poster_url=command.poster_url,
                ticket_url=command.ticket_url,
                start_date=command.start_date,
                end_date=command.end_date,
            )
            hall = exhibit.hall
            hall.revise(
                name=command.hall_name,
                country_code=country.code,
                region=command.region,
                address=command.address,
                opening_hours=command.opening_hours,
                phone=command.phone,
                latitude=command.latitude
                if command.latitude is not None
                else hall.latitude,
                longitude=(
                    command.longitude
                    if command.longitude is not None
                    else hall.longitude
                ),
            )
            exhibit.replace_keywords(keywords)


class DeleteExhibitService(DeleteExhibitUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def delete_exhibit(self, exhibit_id: int) -> None:
        with self._uow as uow:
            if uow.exhibits.find_by_id(exhibit_id) is None:
                raise ExhibitError.not_found()
            uow.exhibits.remove_with_dependents(exhibit_id)


class CreateExhibitService(CreateExhibitUseCase):
    def __init__(
        self,
        *,
        uow: UnitOfWork,
        status_policy: ExhibitStatusPolicy,
        send_push: SendPushUseCase,
    ) -> None:
        self._uow = uow
        self._status_policy = status_policy
        self._send_push = send_push

    def create_exhibit(self, command: CreateExhibitCommand) -> int:
        today = to_service_date(datetime.now(UTC))
        title = command.title.strip()
        hall_name = command.hall_name.strip()
        now = datetime.now(UTC)

        with self._uow as uow:
            country = resolve_country(
                uow, name=command.country_name, is_domestic=command.is_domestic
            )
            keywords = [
                *find_keywords(uow, KeywordType.GENRE, command.genre_names),
                *find_keywords(uow, KeywordType.STYLE, command.style_names),
            ]
            hall = uow.exhibits.find_hall_by_name(hall_name)
            if hall is None:
                hall = new_hall(command, country_code=country.code)
            else:
                hall_id = hall.id
                if hall_id is not None and uow.exhibits.exists_same(
                    hall_id=hall_id, title=title, start_date=command.start_date
                ):
                    raise ExhibitError.duplicate()
                revise_hall(hall, command, country_code=country.code)
            exhibit = new_exhibit(
                command, hall=hall, today=today, policy=self._status_policy
            )
            exhibit.replace_keywords(keywords)

            uow.exhibits.add(exhibit)

            exhibit_id = exhibit.id
            if exhibit_id is None:
                raise RuntimeError("exhibit must be persisted before returning its id")

            recipient_ids = {
                target.user_id for target in uow.device_tokens.find_all_push_targets()
            }
            keyword_ids = [keyword.id for keyword in keywords if keyword.id is not None]
            interested_ids = uow.keywords.find_interested_user_ids(keyword_ids)

            notifications = [
                Notification.exhibit_registered(
                    user_id=user_id,
                    exhibit_id=exhibit_id,
                    hall_name=hall.name,
                    exhibit_title=title,
                    personalized=user_id in interested_ids,
                    now=now,
                )
                for user_id in recipient_ids
            ]
            uow.notifications.add_all(notifications)

        self._push_exhibit_registered(
            exhibit_id=exhibit_id, notifications=notifications
        )
        return exhibit_id

    def _push_exhibit_registered(
        self, *, exhibit_id: int, notifications: list[Notification]
    ) -> None:
        user_ids_by_message: dict[tuple[str, str], list[int]] = defaultdict(list)
        for notification in notifications:
            user_ids_by_message[(notification.title, notification.body)].append(
                notification.user_id
            )

        data = {
            "action": NotificationAction.MOVE_EXHIBIT_DETAIL.value,
            "referenceId": str(exhibit_id),
        }
        for (title, body), user_ids in user_ids_by_message.items():
            try:
                self._send_push.send_push(
                    SendPushCommand(
                        user_ids=tuple(user_ids), title=title, body=body, data=data
                    )
                )
            except Exception:
                _logger.exception("exhibit push failed: exhibit_id=%d", exhibit_id)


def _with_country_code(
    uow: UnitOfWork, search: ExhibitSearch, country_name: str | None
) -> ExhibitSearch:
    if country_name is None:
        return search
    country = uow.locations.find_country_by_name(country_name)
    if country is None:
        raise ExhibitError.unknown_country()
    return replace(search, criteria=replace(search.criteria, country_code=country.code))


def _country_names(uow: UnitOfWork) -> dict[str, str]:
    return {country.code: country.name for country in uow.locations.list_countries()}


def search_exhibit_page(
    uow: UnitOfWork,
    query: SearchExhibitsQuery,
    *,
    today: date,
    policy: ExhibitStatusPolicy,
) -> OffsetPage[ExhibitSearchItem]:
    search = _with_country_code(uow, query.search, query.country_name)
    country_names = _country_names(uow)
    total = uow.exhibits.count_search(search=search, today=today, policy=policy)
    rows = uow.exhibits.search_page(
        search=search,
        today=today,
        policy=policy,
        sort=query.sort,
        direction=query.direction,
        offset=query.page * query.size,
        limit=query.size,
    )
    items = tuple(
        ExhibitSearchItem(
            exhibit_id=exhibit.id,
            title=exhibit.title,
            start_date=exhibit.start_date,
            end_date=exhibit.end_date,
            country_name=country_names.get(
                exhibit.hall.country_code, exhibit.hall.country_code
            ),
            region=exhibit.hall.region,
            genres=exhibit.keyword_names(KeywordType.GENRE),
            status=exhibit.status_on(today=today, policy=policy),
            hall_name=exhibit.hall.name,
        )
        for exhibit in rows
        if exhibit.id is not None
    )
    return OffsetPage(
        items=items, page=query.page, size=query.size, total_elements=total
    )
