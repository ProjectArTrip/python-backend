import secrets
from datetime import UTC, date, datetime

from arttrip.application.domain.exhibit.exhibit import Exhibit
from arttrip.application.domain.exhibit.exhibit_filter import ExhibitFilter
from arttrip.application.domain.exhibit.exhibit_hall import ExhibitHall
from arttrip.application.domain.exhibit.exhibit_services import to_exhibit_summary
from arttrip.application.domain.exhibit.exhibit_status_policy import (
    ExhibitStatusPolicy,
)
from arttrip.application.port.input.exhibit.results import ExhibitSummary
from arttrip.application.port.input.home.queries import (
    ListGenreExhibitsQuery,
    ListTodayExhibitsQuery,
)
from arttrip.application.port.input.home.results import HomeVenue
from arttrip.application.port.input.home.use_cases import (
    ListGenreExhibitsUseCase,
    ListHomeVenuesUseCase,
    ListTodayExhibitsUseCase,
)
from arttrip.application.port.output.today_exhibit_cache_port import (
    TodayExhibitCachePort,
)
from arttrip.application.port.output.unit_of_work import UnitOfWork
from arttrip.application.util.service_date import to_service_date

_random = secrets.SystemRandom()


class ListTodayExhibitsService(ListTodayExhibitsUseCase):
    def __init__(
        self,
        *,
        uow: UnitOfWork,
        cache: TodayExhibitCachePort,
        status_policy: ExhibitStatusPolicy,
        size: int,
    ) -> None:
        self._uow = uow
        self._cache = cache
        self._status_policy = status_policy
        self._size = size

    def list_today_exhibits(
        self, query: ListTodayExhibitsQuery
    ) -> tuple[ExhibitSummary, ...]:
        today = to_service_date(datetime.now(UTC))
        criteria = ExhibitFilter(
            period_start=today,
            period_end=today,
        )
        with self._uow as uow:
            exhibit_ids = self._cache.find(day=today, criteria=criteria)
            if exhibit_ids is None:
                picked = uow.exhibits.pick_random(
                    criteria=criteria,
                    today=today,
                    pivot=_random.random(),
                    limit=self._size,
                )
                exhibit_ids = self._cache.save_if_absent(
                    day=today,
                    criteria=criteria,
                    exhibit_ids=[e.id for e in picked if e.id is not None],
                )
            exhibits = uow.exhibits.find_by_ids(exhibit_ids)
            return _to_summaries(
                uow, exhibits, query.user_id, today, self._status_policy
            )


class ListGenreExhibitsService(ListGenreExhibitsUseCase):
    def __init__(
        self, *, uow: UnitOfWork, status_policy: ExhibitStatusPolicy, size: int
    ) -> None:
        self._uow = uow
        self._status_policy = status_policy
        self._size = size

    def list_genre_exhibits(
        self, query: ListGenreExhibitsQuery
    ) -> tuple[ExhibitSummary, ...]:
        today = to_service_date(datetime.now(UTC))
        with self._uow as uow:
            exhibits = uow.exhibits.pick_random(
                criteria=ExhibitFilter(genre_ids=frozenset({query.genre_id})),
                today=today,
                pivot=_random.random(),
                limit=self._size,
            )
            return _to_summaries(
                uow, exhibits, query.user_id, today, self._status_policy
            )


class ListHomeVenuesService(ListHomeVenuesUseCase):
    def __init__(self, *, uow: UnitOfWork, size: int) -> None:
        self._uow = uow
        self._size = size

    def list_home_venues(self) -> tuple[HomeVenue, ...]:
        today = to_service_date(datetime.now(UTC))
        with self._uow as uow:
            rows = uow.exhibits.list_halls_with_ongoing(today=today, limit=self._size)
            return tuple(_to_home_venue(hall, count) for hall, count in rows)


def _to_home_venue(hall: ExhibitHall, ongoing_exhibit_count: int) -> HomeVenue:
    hall_id = hall.id
    if hall_id is None:
        raise RuntimeError("exhibit hall loaded from storage must have an id")
    return HomeVenue(
        venue_id=hall_id,
        name=hall.name,
        region=hall.region,
        latitude=hall.latitude,
        longitude=hall.longitude,
        ongoing_exhibit_count=ongoing_exhibit_count,
    )


def _to_summaries(
    uow: UnitOfWork,
    exhibits: list[Exhibit],
    user_id: int | None,
    today: date,
    status_policy: ExhibitStatusPolicy,
) -> tuple[ExhibitSummary, ...]:
    favorite_ids: set[int] = set()
    if user_id is not None:
        favorite_ids = uow.favorites.find_exhibit_ids(
            user_id=user_id,
            exhibit_ids=[e.id for e in exhibits if e.id is not None],
        )
    return tuple(
        to_exhibit_summary(
            exhibit,
            status=exhibit.status_on(today=today, policy=status_policy),
            is_favorite=exhibit.id in favorite_ids,
        )
        for exhibit in exhibits
    )
