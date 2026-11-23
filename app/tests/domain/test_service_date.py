from datetime import UTC, date, datetime

import pytest
from arttrip.application.util.exception import DomainException
from arttrip.application.util.service_date import to_service_date


class TestServiceDate:
    @pytest.mark.parametrize(
        ("now", "expected"),
        [
            (datetime(2026, 11, 10, 15, 0, 0, tzinfo=UTC), date(2026, 11, 11)),
            (datetime(2026, 11, 10, 14, 59, 59, tzinfo=UTC), date(2026, 11, 10)),
            (datetime(2026, 11, 10, 23, 59, 59, tzinfo=UTC), date(2026, 11, 11)),
        ],
    )
    def test_자정_경계에서_한국_날짜를_돌려준다(
        self, now: datetime, expected: date
    ) -> None:
        # given
        # when
        today = to_service_date(now)

        # then
        assert today == expected

    def test_시간대_없는_시각은_거부한다(self) -> None:
        # given
        naive_now = datetime(2026, 11, 11, 0, 0)

        # when
        with pytest.raises(DomainException) as raised:
            to_service_date(naive_now)

        # then
        assert raised.value.code == "DATETIME_NAIVE"
