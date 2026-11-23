import pytest
from arttrip.application.domain.user.display_name import (
    ANIMAL_NAMES,
    generate_display_name,
)
from arttrip.application.util.exception import DomainException

NAME_MAX_LENGTH = 255


class TestGenerateDisplayName:
    def test_목록이_비면_예외(self) -> None:
        # given
        # when

        # then
        with pytest.raises(DomainException):
            generate_display_name(pool=[])

    @pytest.mark.parametrize("digit_count", [1, 4, 10])
    def test_접미사_자리수가_항상_고정된다(self, digit_count: int) -> None:
        # given
        expected = len("판다") + digit_count

        # when
        lengths = {
            len(generate_display_name(pool=["판다"], digit_count=digit_count))
            for _ in range(500)
        }

        # then
        assert lengths == {expected}

    def test_기본_목록이_칼럼_상한을_넘지_않는다(self) -> None:
        # given
        longest = max(len(name) for name in ANIMAL_NAMES)

        # when
        generated = generate_display_name()

        # then
        assert longest + 4 <= NAME_MAX_LENGTH
        assert len(generated) <= NAME_MAX_LENGTH
