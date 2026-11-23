import pytest
from arttrip.application.domain.exhibit.country import Country
from arttrip.application.domain.exhibit.exhibit_hall import DEFAULT_COUNTRY_CODE
from arttrip.application.util.exception import DomainException


class TestCountry:
    # 막는 것: 국내 나라가 해외 필터 칩에 섞여, 해외 필터로 국내 전시가 나오는 것 (경계).
    def test_국내_코드를_가진_나라만_국내다(self) -> None:
        # given
        domestic = Country(
            id_=1, code=DEFAULT_COUNTRY_CODE, name="한국", display_order=0
        )
        overseas = Country(id_=2, code="FR", name="프랑스", display_order=1)

        # when
        # then
        assert domestic.is_domestic is True
        assert overseas.is_domestic is False

    def test_해외로_표시한_전시에_한국을_고르면_거부한다(self) -> None:
        # given
        korea = Country(id_=1, code=DEFAULT_COUNTRY_CODE, name="한국", display_order=0)

        # when
        with pytest.raises(DomainException) as raised:
            korea.ensure_overseas()

        # then
        assert raised.value.code == "EXHIBIT_COUNTRY_DOMESTIC_MISMATCH"
