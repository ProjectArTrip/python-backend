from datetime import date

import pytest
from arttrip.application.domain.curation.curation import Curation
from arttrip.application.domain.curation.refresh_cycle import RefreshCycle
from arttrip.application.domain.curation.sort_type import SortType
from arttrip.application.util.exception import DomainException

VISIBLE_FROM = date(2026, 11, 1)
VISIBLE_TO = date(2026, 11, 30)


def curation(*, active: bool) -> Curation:
    return Curation(
        id_=1,
        title="파리 현대미술 완전 정복!",
        active=active,
        visible_from=VISIBLE_FROM,
        visible_to=VISIBLE_TO,
        refresh_cycle=RefreshCycle.MONTHLY,
        sort_type=SortType.NONE,
    )


def create_curation(
    *,
    visible_from: date = VISIBLE_FROM,
    visible_to: date = VISIBLE_TO,
    exhibit_ids: tuple[int, ...] = (1, 2),
) -> Curation:
    return Curation.create(
        title="파리 현대미술 완전 정복!",
        refresh_cycle=RefreshCycle.MONTHLY,
        sort_type=SortType.NONE,
        visible_from=visible_from,
        visible_to=visible_to,
        active=True,
        exhibit_ids=exhibit_ids,
    )


class TestCuration:
    def test_꺼_둔_큐레이션은_보이지_않는다(self) -> None:
        # given
        hidden_curation = curation(active=False)

        # when
        visible = hidden_curation.is_visible

        # then
        assert visible is False

    def test_노출_기간이_지나도_켜져_있으면_보인다(self) -> None:
        # given
        expired_but_active = curation(active=True)
        day_after_visible_to = date(2026, 12, 1)

        # when
        visible = expired_but_active.is_visible

        # then
        assert day_after_visible_to > VISIBLE_TO
        assert visible is True

    def test_노출_시작일이_종료일보다_늦으면_만들_수_없다(self) -> None:
        # given
        day_after_end = date(2026, 12, 1)

        # when
        with pytest.raises(DomainException) as raised:
            create_curation(visible_from=day_after_end, visible_to=VISIBLE_TO)

        # then
        assert raised.value.code == "CURATION_PERIOD_INVALID"

    def test_같은_전시를_두_번_담을_수_없다(self) -> None:
        # given
        duplicated_ids = (1, 2, 1)

        # when
        with pytest.raises(DomainException) as raised:
            create_curation(exhibit_ids=duplicated_ids)

        # then
        assert raised.value.code == "CURATION_EXHIBIT_DUPLICATE"

    def test_전시_없이는_만들_수_없다(self) -> None:
        # when
        with pytest.raises(DomainException) as raised:
            create_curation(exhibit_ids=())

        # then
        assert raised.value.code == "CURATION_EXHIBITS_REQUIRED"

    def test_전시를_다시_담으면_이전_전시는_빠지고_순서가_0부터_다시_매겨진다(
        self,
    ) -> None:
        # given
        curation_with_three = create_curation(exhibit_ids=(1, 2, 3))

        # when
        curation_with_three.replace_exhibits((3, 1))

        # then
        assert [
            (e.exhibit_id, e.display_order) for e in curation_with_three.exhibits
        ] == [
            (3, 0),
            (1, 1),
        ]

    def test_검증에_실패한_수정은_기존_값을_바꾸지_않는다(self) -> None:
        # given
        original = create_curation()
        day_after_end = date(2026, 12, 1)

        # when
        with pytest.raises(DomainException):
            original.revise(
                title="바뀐 제목",
                refresh_cycle=RefreshCycle.BIWEEKLY,
                sort_type=SortType.LATEST,
                visible_from=day_after_end,
                visible_to=VISIBLE_TO,
                active=False,
            )

        # then
        assert original.title == "파리 현대미술 완전 정복!"
        assert original.visible_from == VISIBLE_FROM
        assert original.active is True
