from datetime import UTC, datetime

import pytest
from arttrip.application.domain.exhibit.recent_exhibit import (
    get_recent_exhibit_retention_start,
)
from arttrip.application.util.exception import DomainException

NOW = datetime(2026, 11, 11, 12, 0, tzinfo=UTC)
RETENTION_DAYS = 14


class TestRecentExhibit:
    def test_보관_시작_시각은_정확히_보관_기간만큼_전이다(self) -> None:
        # given
        # when
        start = get_recent_exhibit_retention_start(NOW, days=RETENTION_DAYS)
        # then
        assert (NOW - start).seconds == 0
        assert (NOW - start).days == RETENTION_DAYS

    def test_시간대_없는_시각은_거부한다(self) -> None:
        # given
        naive_now = datetime(2026, 11, 11, 12, 0)

        # when
        with pytest.raises(DomainException) as raised:
            get_recent_exhibit_retention_start(naive_now, days=RETENTION_DAYS)

        # then
        assert raised.value.code == "DATETIME_NAIVE"
