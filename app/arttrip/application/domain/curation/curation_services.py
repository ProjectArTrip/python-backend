import secrets
from datetime import UTC, datetime
from typing import Final

from arttrip.application.domain.curation.exceptions import CurationError
from arttrip.application.domain.exhibit.exhibit_filter import ExhibitFilter
from arttrip.application.domain.exhibit.exhibit_services import to_exhibit_summary
from arttrip.application.domain.exhibit.exhibit_status_policy import (
    ExhibitStatusPolicy,
)
from arttrip.application.port.input.curation.queries import (
    GetCurationQuery,
    PickCurationQuery,
)
from arttrip.application.port.input.curation.results import (
    CurationDetail,
    CurationSummary,
)
from arttrip.application.port.input.curation.use_cases import (
    GetCurationUseCase,
    PickCurationUseCase,
)
from arttrip.application.port.input.pagination import CursorPage
from arttrip.application.port.output.unit_of_work import UnitOfWork
from arttrip.application.util.service_date import to_service_date

_random = secrets.SystemRandom()
_EXHIBIT_POOL_LIMIT: Final = 100


class GetCurationService(GetCurationUseCase):
    def __init__(self, *, uow: UnitOfWork, status_policy: ExhibitStatusPolicy) -> None:
        self._uow = uow
        self._status_policy = status_policy

    def get_curation(self, query: GetCurationQuery) -> CurationDetail:
        today = to_service_date(datetime.now(UTC))
        with self._uow as uow:
            curation = uow.curations.find_by_id(query.curation_id)
            if curation is None or not curation.is_visible:
                raise CurationError.not_found()

            rows = uow.curations.list_exhibits_page(
                curation_id=query.curation_id,
                cursor=query.cursor,
                limit=query.size + 1,
                today=today,
            )
            has_next = len(rows) > query.size
            page_rows = rows[: query.size]
            next_cursor = page_rows[-1].display_order if has_next else None

            favorite_ids: set[int] = set()
            if query.user_id is not None:
                favorite_ids = uow.favorites.find_exhibit_ids(
                    user_id=query.user_id,
                    exhibit_ids=[r.exhibit.id for r in page_rows if r.exhibit.id],
                )
            items = tuple(
                to_exhibit_summary(
                    row.exhibit,
                    status=row.exhibit.status_on(
                        today=today, policy=self._status_policy
                    ),
                    is_favorite=row.exhibit.id in favorite_ids,
                )
                for row in page_rows
            )
            return CurationDetail(
                curation_id=query.curation_id,
                title=curation.title,
                page=CursorPage(items=items, next_cursor=next_cursor),
            )


class PickCurationService(PickCurationUseCase):
    def __init__(
        self, *, uow: UnitOfWork, status_policy: ExhibitStatusPolicy, size: int
    ) -> None:
        self._uow = uow
        self._status_policy = status_policy
        self._size = size

    def pick_curation(self, query: PickCurationQuery) -> CurationSummary:
        today = to_service_date(datetime.now(UTC))
        criteria = ExhibitFilter(
            domestic=query.domestic, country_code=query.country_code
        )
        with self._uow as uow:
            candidate_ids = uow.curations.list_visible_ids(
                today=today, criteria=criteria
            )
            if not candidate_ids:
                raise CurationError.not_found()
            curation_id = _random.choice(candidate_ids)
            curation = uow.curations.find_by_id(curation_id)
            if curation is None:
                raise CurationError.not_found()

            pool = uow.curations.list_matching_exhibits(
                curation_id=curation_id,
                criteria=criteria,
                limit=_EXHIBIT_POOL_LIMIT,
                today=today,
            )

            exhibits = _random.sample(pool, k=min(self._size, len(pool)))

            favorite_ids: set[int] = set()
            if query.user_id is not None:
                favorite_ids = uow.favorites.find_exhibit_ids(
                    user_id=query.user_id,
                    exhibit_ids=[e.id for e in exhibits if e.id is not None],
                )
            return CurationSummary(
                curation_id=curation_id,
                title=curation.title,
                exhibits=tuple(
                    to_exhibit_summary(
                        exhibit,
                        status=exhibit.status_on(
                            today=today, policy=self._status_policy
                        ),
                        is_favorite=exhibit.id in favorite_ids,
                    )
                    for exhibit in exhibits
                ),
            )
