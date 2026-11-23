from arttrip.application.domain.keyword.keyword import Keyword


class TestKeyword:
    def test_전각_공백과_탭이_섞여도_같은_이름으로_본다(self) -> None:
        # given
        typed = " 근대\u3000미술\t"

        # when
        normalized = Keyword.normalize_name(typed)

        # then
        assert normalized == Keyword.normalize_name("근대 미술")
        assert normalized == "근대미술"
