import logging
from datetime import date, datetime, time, timedelta
from typing import Final

from redis import Redis, RedisError

from arttrip.application.domain.exhibit.exhibit_filter import ExhibitFilter
from arttrip.application.port.output.today_exhibit_cache_port import (
    TodayExhibitCachePort,
)
from arttrip.application.util.service_date import SERVICE_TIMEZONE

KEY_PREFIX: Final = "home:today:"
ID_SEPARATOR: Final = ","

_logger = logging.getLogger(__name__)


class RedisTodayExhibitCacheAdapter(TodayExhibitCachePort):
    def __init__(self, *, client: Redis) -> None:
        self._client = client

    def find(self, *, day: date, criteria: ExhibitFilter) -> list[int] | None:
        try:
            cached = self._client.get(self._key(day, criteria))
        except RedisError:
            _logger.warning("today exhibit cache read failed", exc_info=True)
            return None
        return _decode(cached) if isinstance(cached, str) else None

    def save_if_absent(
        self, *, day: date, criteria: ExhibitFilter, exhibit_ids: list[int]
    ) -> list[int]:
        try:
            previous = self._client.set(
                self._key(day, criteria),
                ID_SEPARATOR.join(map(str, exhibit_ids)),
                nx=True,
                get=True,
                exat=_next_service_midnight(day),
            )
        except RedisError:
            _logger.warning("today exhibit cache write failed", exc_info=True)
            return exhibit_ids
        return _decode(previous) if isinstance(previous, str) else exhibit_ids

    @staticmethod
    def _key(day: date, criteria: ExhibitFilter) -> str:
        return (
            f"{KEY_PREFIX}{day.isoformat()}"
            f":{criteria.domestic}:{criteria.country_code}:{','.join(sorted(criteria.regions))}"
        )


def _decode(raw: str) -> list[int]:
    return [int(value) for value in raw.split(ID_SEPARATOR) if value]


def _next_service_midnight(day: date) -> int:
    midnight = datetime.combine(day + timedelta(days=1), time.min, SERVICE_TIMEZONE)
    return int(midnight.timestamp())
