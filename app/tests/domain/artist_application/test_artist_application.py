from datetime import UTC, datetime

import pytest
from arttrip.application.domain.artist_application.artist_application import (
    INTRODUCTION_MAX_LENGTH,
    REJECTION_REASON_MAX_LENGTH,
    ArtistApplication,
)
from arttrip.application.domain.artist_application.artist_application_status import (
    ArtistApplicationStatus,
)
from arttrip.application.util.exception import DomainException

NOW = datetime(2026, 11, 11, 12, 0, tzinfo=UTC)
LATER = datetime(2026, 11, 12, 12, 0, tzinfo=UTC)
ADMIN_ID = 99


def pending() -> ArtistApplication:
    return ArtistApplication.submit(
        user_id=1, introduction="회화 작가입니다.", portfolio_url=None, now=NOW
    )


class TestArtistApplication:
    def test_승인된_신청은_다시_심사할_수_없다(self) -> None:
        # given
        application = pending()
        application.approve(reviewer_id=ADMIN_ID, now=NOW)

        # when
        with pytest.raises(DomainException) as raised:
            application.reject(reviewer_id=ADMIN_ID, reason="번복", now=LATER)

        # then
        assert raised.value.code == "ARTIST_REQUEST_ALREADY_REVIEWED"
        assert application.status is ArtistApplicationStatus.APPROVED
        assert application.rejection_reason is None

    def test_반려된_신청은_승인할_수_없다(self) -> None:
        # given
        application = pending()
        application.reject(reviewer_id=ADMIN_ID, reason="증빙 부족", now=NOW)

        # when
        with pytest.raises(DomainException) as raised:
            application.approve(reviewer_id=ADMIN_ID, now=LATER)

        # then
        assert raised.value.code == "ARTIST_REQUEST_ALREADY_REVIEWED"
        assert application.status is ArtistApplicationStatus.REJECTED
        assert application.reviewed_at == NOW

    @pytest.mark.parametrize(
        "reason", ["", "   ", "가" * (REJECTION_REASON_MAX_LENGTH + 1)]
    )
    def test_반려_사유가_없거나_너무_길면_반려할_수_없다(self, reason: str) -> None:
        # given
        application = pending()

        # when
        with pytest.raises(DomainException) as raised:
            application.reject(reviewer_id=ADMIN_ID, reason=reason, now=LATER)

        # then
        assert raised.value.code == "ARTIST_REQUEST_REJECTION_REASON_REQUIRED"
        assert application.status is ArtistApplicationStatus.PENDING

    @pytest.mark.parametrize(
        "introduction", ["", "   ", "가" * (INTRODUCTION_MAX_LENGTH + 1)]
    )
    def test_소개글이_비었거나_너무_길면_신청할_수_없다(
        self, introduction: str
    ) -> None:
        # given
        # when
        with pytest.raises(DomainException) as raised:
            ArtistApplication.submit(
                user_id=1, introduction=introduction, portfolio_url=None, now=NOW
            )

        # then
        assert raised.value.code == "ARTIST_REQUEST_INTRODUCTION_INVALID"

    @pytest.mark.parametrize(
        "portfolio_url",
        [
            "javascript:alert(1)",
            "http://example.com/portfolio",
            "data:text/html,<script>alert(1)</script>",
            "//example.com",
            "https://" + "a" * 1024,
        ],
    )
    def test_https_가_아닌_포트폴리오_주소는_거부한다(self, portfolio_url: str) -> None:
        # given
        # when
        with pytest.raises(DomainException) as raised:
            ArtistApplication.submit(
                user_id=1,
                introduction="회화 작가입니다.",
                portfolio_url=portfolio_url,
                now=NOW,
            )

        # then
        assert raised.value.code == "ARTIST_REQUEST_PORTFOLIO_URL_INVALID"
