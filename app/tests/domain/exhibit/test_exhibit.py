from datetime import date
from decimal import Decimal

import pytest
from arttrip.application.domain.exhibit.exhibit import Exhibit
from arttrip.application.domain.exhibit.exhibit_hall import ExhibitHall
from arttrip.application.domain.exhibit.exhibit_status import ExhibitStatus
from arttrip.application.domain.exhibit.exhibit_status_policy import (
    ExhibitStatusPolicy,
)
from arttrip.application.util.exception import DomainException

POLICY = ExhibitStatusPolicy(ending_soon_days=7)
START = date(2026, 11, 10)
END = date(2026, 11, 30)


def exhibit_between(start_date: date | None, end_date: date | None) -> Exhibit:
    hall = ExhibitHall(
        id_=1,
        name="오르세 미술관",
        address=None,
        phone=None,
        region="파리",
        country_code="FR",
        homepage_url=None,
        latitude=Decimal("48.8600"),
        longitude=Decimal("2.3266"),
        opening_hours=None,
        closed_days=None,
    )
    return Exhibit(
        id_=1,
        hall=hall,
        title="Imagination in Bloom",
        description=None,
        poster_url=None,
        ticket_url=None,
        status=ExhibitStatus.FINISHED,
        start_date=start_date,
        end_date=end_date,
    )


class TestExhibit:
    @pytest.mark.parametrize(
        ("today", "expected"),
        [
            (date(2026, 11, 9), ExhibitStatus.UPCOMING),  # 시작 전날
            (date(2026, 11, 10), ExhibitStatus.ONGOING),  # 시작 당일
            (date(2026, 11, 22), ExhibitStatus.ONGOING),  # 종료 8일 전
            (date(2026, 11, 23), ExhibitStatus.ENDING_SOON),  # 종료 7일 전
            (date(2026, 11, 30), ExhibitStatus.ENDING_SOON),  # 종료 당일
            (date(2026, 12, 1), ExhibitStatus.FINISHED),  # 종료 다음 날
        ],
    )
    def test_경계_날짜에서_상태가_정확히_바뀐다(
        self, today: date, expected: ExhibitStatus
    ) -> None:
        # given
        exhibit = exhibit_between(START, END)

        # when
        status = exhibit.status_on(today=today, policy=POLICY)

        # then
        assert status is expected

    def test_시작_전이면_종료가_가까워도_예정이다(self) -> None:
        # given
        exhibit = exhibit_between(date(2026, 11, 20), date(2026, 11, 22))

        # when
        status = exhibit.status_on(today=date(2026, 11, 19), policy=POLICY)

        # then
        assert status is ExhibitStatus.UPCOMING

    @pytest.mark.parametrize(
        ("start_date", "end_date"),
        [(None, None), (START, None), (None, date(2027, 12, 31))],
    )
    def test_날짜가_비어_있어도_진행중으로_판정한다(
        self, start_date: date | None, end_date: date | None
    ) -> None:
        # given
        exhibit = exhibit_between(start_date, end_date)

        # when
        status = exhibit.status_on(today=date(2026, 11, 15), policy=POLICY)

        # then
        assert status is ExhibitStatus.ONGOING

    def test_마감임박_기준은_음수일_수_없다(self) -> None:
        # given
        # when
        # then
        with pytest.raises(ValueError):
            ExhibitStatusPolicy(ending_soon_days=-1)

    def test_시작일이_종료일보다_늦게는_수정할_수_없다(self) -> None:
        # given
        exhibit = exhibit_between(START, END)

        # when
        with pytest.raises(DomainException) as raised:
            exhibit.revise(
                title="제목",
                description=None,
                poster_url=None,
                ticket_url=None,
                start_date=END,
                end_date=START,
            )

            # then
            assert raised.value.code == "EXHIBIT_SCHEDULE_INVALID"
            assert exhibit.start_date == START

    def test_공백뿐인_제목으로는_수정할_수_없다(self) -> None:
        # given
        exhibit = exhibit_between(START, END)

        # when
        with pytest.raises(DomainException) as raised:
            exhibit.revise(
                title="   ",
                description=None,
                poster_url=None,
                ticket_url=None,
                start_date=START,
                end_date=END,
            )

        # then
        assert raised.value.code == "EXHIBIT_TITLE_REQUIRED"

    @pytest.mark.parametrize(
        ("latitude", "longitude"),
        [
            (Decimal("90.0000001"), Decimal("0")),  # 위도 상한 바로 위
            (Decimal("-90.0000001"), Decimal("0")),  # 위도 하한 바로 아래
            (Decimal("0"), Decimal("180.0000001")),  # 경도 상한 바로 위
        ],
    )
    def test_범위를_벗어난_좌표로는_전시관을_수정할_수_없다(
        self, latitude: Decimal, longitude: Decimal
    ) -> None:
        # given
        hall = exhibit_between(START, END).hall

        # when
        with pytest.raises(DomainException) as raised:
            hall.revise(
                name="오르세 미술관",
                country_code="FR",
                region="파리",
                address=None,
                opening_hours=None,
                phone=None,
                latitude=latitude,
                longitude=longitude,
            )

        # then
        assert raised.value.code == "EXHIBIT_HALL_COORDINATES_INVALID"

    def test_끝난_날짜로_등록하면_종료_상태로_저장된다(self) -> None:
        # given
        hall = exhibit_between(START, END).hall
        day_after_end = date(2026, 12, 1)

        # when
        exhibit = Exhibit.create(
            hall=hall,
            title="지난 전시",
            description=None,
            poster_url=None,
            ticket_url=None,
            start_date=START,
            end_date=END,
            today=day_after_end,
            policy=POLICY,
        )

        # then
        assert exhibit.status is ExhibitStatus.FINISHED

    def test_범위를_벗어난_좌표로는_전시관을_만들_수_없다(self) -> None:
        # given
        latitude_above_limit = Decimal("90.0000001")

        # when
        with pytest.raises(DomainException) as raised:
            ExhibitHall.create(
                name="새 전시관",
                country_code="FR",
                region="파리",
                address=None,
                opening_hours=None,
                phone=None,
                latitude=latitude_above_limit,
                longitude=Decimal("0"),
            )

        # then
        assert raised.value.code == "EXHIBIT_HALL_COORDINATES_INVALID"

    def test_다른_사람의_전시는_소유자로_인정하지_않는다(self) -> None:
        # given
        exhibit = exhibit_between(date(2026, 11, 1), date(2026, 12, 1))
        exhibit.owner_id = 1

        # when
        with pytest.raises(DomainException) as raised:
            exhibit.ensure_owned_by(2)

        # then
        assert raised.value.code == "EXHIBIT_NOT_FOUND"

    def test_등록자가_없는_전시는_누구의_것도_아니다(self) -> None:
        # given
        exhibit = exhibit_between(date(2026, 11, 1), date(2026, 12, 1))

        # when
        with pytest.raises(DomainException) as raised:
            exhibit.ensure_owned_by(1)

        # then
        assert raised.value.code == "EXHIBIT_NOT_FOUND"
