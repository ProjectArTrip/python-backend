import secrets
from datetime import UTC, date, datetime

from arttrip.application.domain.exhibit.exhibit import Exhibit
from arttrip.application.domain.exhibit.exhibit_filter import ExhibitFilter
from arttrip.application.domain.exhibit.exhibit_list_sort import ExhibitListSort
from arttrip.application.domain.exhibit.exhibit_services import to_exhibit_summary
from arttrip.application.domain.exhibit.exhibit_status_policy import (
    ExhibitStatusPolicy,
)
from arttrip.application.domain.exhibit.location_services import ensure_known_location
from arttrip.application.domain.keyword.keyword_type import KeywordType
from arttrip.application.domain.user.current_user import load_current_user
from arttrip.application.port.input.exhibit.results import ExhibitSummary
from arttrip.application.port.input.home.queries import (
    ListGenreExhibitsQuery,
    ListPersonalizedExhibitsQuery,
    ListScheduledExhibitsQuery,
    ListTodayExhibitsQuery,
)
from arttrip.application.port.input.home.use_cases import (
    ListGenreExhibitsUseCase,
    ListPersonalizedExhibitsUseCase,
    ListScheduledExhibitsUseCase,
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
            domestic=query.domestic,
            country_code=query.country_code,
            regions=_as_regions(query.region),
        )
        with self._uow as uow:
            ensure_known_location(
                uow,
                country_code=query.country_code,
                regions=_as_regions(query.region),
            )
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


class ListScheduledExhibitsService(ListScheduledExhibitsUseCase):
    def __init__(
        self, *, uow: UnitOfWork, status_policy: ExhibitStatusPolicy, size: int
    ) -> None:
        self._uow = uow
        self._status_policy = status_policy
        self._size = size

    def list_scheduled_exhibits(
        self, query: ListScheduledExhibitsQuery
    ) -> tuple[ExhibitSummary, ...]:
        today = to_service_date(datetime.now(UTC))
        criteria = ExhibitFilter(
            period_start=query.scheduled_date,
            period_end=query.scheduled_date,
            domestic=query.domestic,
            country_code=query.country_code,
            regions=_as_regions(query.region),
        )
        with self._uow as uow:
            ensure_known_location(
                uow, country_code=query.country_code, regions=criteria.regions
            )
            exhibits = uow.exhibits.pick_random(
                criteria=criteria,
                today=today,
                pivot=_random.random(),
                limit=self._size,
            )
            return _to_summaries(
                uow, exhibits, query.user_id, today, self._status_policy
            )


class ListPersonalizedExhibitsService(ListPersonalizedExhibitsUseCase):
    def __init__(
        self, *, uow: UnitOfWork, status_policy: ExhibitStatusPolicy, size: int
    ) -> None:
        self._uow = uow
        self._status_policy = status_policy
        self._size = size

    def list_personalized_exhibits(
        self, query: ListPersonalizedExhibitsQuery
    ) -> tuple[ExhibitSummary, ...]:
        today = to_service_date(datetime.now(UTC))
        regions = _as_regions(query.region)
        with self._uow as uow:
            ensure_known_location(uow, country_code=query.country_code, regions=regions)
            user = load_current_user(uow.users, query.user_id)

            keywords = uow.keywords.find_by_ids({k.keyword_id for k in user.keywords})

            genre_ids = frozenset(
                k.id
                for k in keywords
                if k.id is not None and k.keyword_type is KeywordType.GENRE
            )
            style_ids = frozenset(
                k.id
                for k in keywords
                if k.id is not None and k.keyword_type is KeywordType.STYLE
            )
            exhibits = uow.exhibits.pick_random(
                criteria=ExhibitFilter(
                    domestic=query.domestic,
                    country_code=query.country_code,
                    regions=regions,
                    genre_ids=genre_ids,
                    style_ids=style_ids,
                ),
                today=today,
                pivot=_random.random(),
                limit=self._size,
            )

            if not exhibits:
                exhibits = [
                    exhibit
                    for exhibit, _ in uow.exhibits.list_page(
                        criteria=ExhibitFilter(
                            period_start=today,
                            domestic=query.domestic,
                            country_code=query.country_code,
                            regions=regions,
                        ),
                        sort=ExhibitListSort.LATEST,
                        cursor=None,
                        limit=self._size,
                    )
                ]
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


def _as_regions(region: str | None) -> frozenset[str]:
    return frozenset({region}) if region is not None else frozenset()
