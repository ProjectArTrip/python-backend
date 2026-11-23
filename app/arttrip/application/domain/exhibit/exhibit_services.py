from datetime import UTC, datetime

from arttrip.application.domain.exhibit.exceptions import ExhibitError
from arttrip.application.domain.exhibit.exhibit import Exhibit
from arttrip.application.domain.exhibit.exhibit_status import ExhibitStatus
from arttrip.application.domain.exhibit.exhibit_status_policy import ExhibitStatusPolicy
from arttrip.application.domain.exhibit.location_services import ensure_known_location
from arttrip.application.domain.exhibit.recent_exhibit import (
    get_recent_exhibit_retention_start,
)
from arttrip.application.port.input.exhibit.queries import (
    GetExhibitQuery,
    ListExhibitsQuery,
    ListRecentExhibitsQuery,
)
from arttrip.application.port.input.exhibit.results import (
    ExhibitDetail,
    ExhibitHallSummary,
    ExhibitHallView,
    ExhibitPage,
    ExhibitSummary,
)
from arttrip.application.port.input.exhibit.use_cases import (
    GetExhibitUseCase,
    ListExhibitsUseCase,
    ListRecentExhibitsUseCase,
)
from arttrip.application.port.output.unit_of_work import UnitOfWork
from arttrip.application.util.service_date import to_service_date


class GetExhibitService(GetExhibitUseCase):
    def __init__(self, *, uow: UnitOfWork, status_policy: ExhibitStatusPolicy) -> None:
        self._uow = uow
        self._status_policy = status_policy

    def get_exhibit(self, query: GetExhibitQuery) -> ExhibitDetail:
        today = to_service_date(datetime.now(UTC))
        now = datetime.now(UTC)

        with self._uow as uow:
            exhibit = uow.exhibits.find_by_id(query.exhibit_id)

            if exhibit is None:
                raise ExhibitError.not_found()

            uow.exhibits.increment_view_count(query.exhibit_id)

            uow.recent_exhibits.record(
                user_id=query.user_id, exhibit_id=query.exhibit_id, viewed_at=now
            )

            status = exhibit.status_on(today=today, policy=self._status_policy)
            favorite_ids = uow.favorites.find_exhibit_ids(
                user_id=query.user_id, exhibit_ids=[query.exhibit_id]
            )

            review_count = uow.reviews.count_approved(exhibit_id=query.exhibit_id)
            return _to_detail(
                exhibit,
                status=status,
                is_favorite=query.exhibit_id in favorite_ids,
                review_count=review_count,
            )


class ListExhibitsService(ListExhibitsUseCase):
    def __init__(self, *, uow: UnitOfWork, status_policy: ExhibitStatusPolicy) -> None:
        self._uow = uow
        self._status_policy = status_policy

    def list_exhibits(self, query: ListExhibitsQuery) -> ExhibitPage:
        today = to_service_date(datetime.now(UTC))

        with self._uow as uow:
            ensure_known_location(
                uow,
                country_code=query.criteria.country_code,
                regions=query.criteria.regions,
            )
            rows = uow.exhibits.list_page(
                criteria=query.criteria,
                sort=query.sort,
                cursor=query.cursor,
                limit=query.size + 1,
            )
            page = rows[: query.size]
            page_exhibits = [exhibit for exhibit, _ in page]
            favorite_ids = uow.favorites.find_exhibit_ids(
                user_id=query.user_id,
                exhibit_ids=[e.id for e in page_exhibits if e.id is not None],
            )
            items = tuple(
                to_exhibit_summary(
                    exhibit,
                    status=exhibit.status_on(today=today, policy=self._status_policy),
                    is_favorite=exhibit.id in favorite_ids,
                )
                for exhibit in page_exhibits
            )
            next_cursor = page[-1][1] if len(rows) > query.size else None
            return ExhibitPage(items=items, next_cursor=next_cursor)


class ListRecentExhibitsService(ListRecentExhibitsUseCase):
    def __init__(
        self,
        *,
        uow: UnitOfWork,
        status_policy: ExhibitStatusPolicy,
        size: int,
        retention_days: int,
    ) -> None:
        self._uow = uow
        self._status_policy = status_policy
        self._size = size
        self._retention_days = retention_days

    def list_recent_exhibits(
        self, query: ListRecentExhibitsQuery
    ) -> tuple[ExhibitSummary, ...]:
        now = datetime.now(UTC)
        today = to_service_date(now)

        with self._uow as uow:
            exhibits = uow.recent_exhibits.list_exhibits(
                user_id=query.user_id,
                since=get_recent_exhibit_retention_start(
                    now, days=self._retention_days
                ),
                limit=self._size,
            )
            favorite_ids = uow.favorites.find_exhibit_ids(
                user_id=query.user_id,
                exhibit_ids=[e.id for e in exhibits if e.id is not None],
            )
            return tuple(
                to_exhibit_summary(
                    exhibit,
                    status=exhibit.status_on(today=today, policy=self._status_policy),
                    is_favorite=exhibit.id in favorite_ids,
                )
                for exhibit in exhibits
            )


def _to_detail(
    exhibit: Exhibit, status: ExhibitStatus, is_favorite: bool, review_count: int
) -> ExhibitDetail:
    exhibit_id = exhibit.id
    if exhibit_id is None:
        raise RuntimeError("exhibit loaded from storage must have an id")
    hall = exhibit.hall
    return ExhibitDetail(
        exhibit_id=exhibit_id,
        title=exhibit.title,
        description=exhibit.description,
        poster_url=exhibit.poster_url,
        ticket_url=exhibit.ticket_url,
        status=status,
        start_date=exhibit.start_date,
        end_date=exhibit.end_date,
        hall=ExhibitHallView(
            name=hall.name,
            address=hall.address,
            phone=hall.phone,
            homepage_url=hall.homepage_url,
            opening_hours=hall.opening_hours,
            closed_days=hall.closed_days,
            region=hall.region,
            country_code=hall.country_code,
            latitude=hall.latitude,
            longitude=hall.longitude,
        ),
        is_favorite=is_favorite,
        review_count=review_count,
    )


def to_exhibit_summary(
    exhibit: Exhibit, status: ExhibitStatus, is_favorite: bool
) -> ExhibitSummary:
    exhibit_id = exhibit.id
    if exhibit_id is None:
        raise RuntimeError("exhibit loaded from storage must have an id")
    return ExhibitSummary(
        exhibit_id=exhibit_id,
        title=exhibit.title,
        poster_url=exhibit.poster_url,
        status=status,
        start_date=exhibit.start_date,
        end_date=exhibit.end_date,
        hall=ExhibitHallSummary(
            name=exhibit.hall.name,
            region=exhibit.hall.region,
            country_code=exhibit.hall.country_code,
        ),
        is_favorite=is_favorite,
    )
