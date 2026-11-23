from datetime import datetime

import pytest
from arttrip.application.domain.favorite.favorite import Favorite
from arttrip.application.util.exception import DomainException

NAIVE_NOW = datetime(2026, 11, 11, 12, 0)


class TestFavorite:
    def test_시간대_없는_시각으로는_생성_불가능(self) -> None:
        # given
        # when
        with pytest.raises(DomainException) as raised:
            Favorite.create(user_id=1, exhibit_id=1, now=NAIVE_NOW)

        # then
        assert raised.value.code == "DATETIME_NAIVE"
