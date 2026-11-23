from datetime import date

import pytest
from arttrip.application.domain.exhibit.exhibit_filter import ExhibitFilter
from arttrip.application.util.exception import DomainException


class TestExhibitFilter:
    def test_기간이_뒤집히면_거부한다(self) -> None:
        # given
        # when
        with pytest.raises(DomainException) as raised:
            ExhibitFilter(period_start=date(2026, 12, 2), period_end=date(2026, 12, 1))

        # then
        assert raised.value.code == "EXHIBIT_PERIOD_INVALID"

    def test_시작일과_종료일이_같으면_허용한다(self) -> None:
        # given
        same_day = date(2026, 12, 1)

        # when
        criteria = ExhibitFilter(period_start=same_day, period_end=same_day)

        # then
        assert criteria.period_start == criteria.period_end

    def test_해외_조회에_지역입력_시_예외(self) -> None:
        # given
        # when
        with pytest.raises(DomainException) as raised:
            ExhibitFilter(domestic=False, regions=frozenset({"서울"}))

        # then
        assert raised.value.code == "EXHIBIT_REGION_REQUIRES_DOMESTIC"

    def test_국내_조회에_해외_국가_선택_시_예외(self) -> None:
        # given
        # when
        with pytest.raises(DomainException) as raised:
            ExhibitFilter(domestic=True, country_code="JP")

        # then
        assert raised.value.code == "EXHIBIT_COUNTRY_CONFLICTS_WITH_DOMESTIC"
