from datetime import UTC, datetime, timedelta, timezone

import pytest
from arttrip.application.domain.auth.social_provider import SocialProvider
from arttrip.application.domain.user.profile_image_policy import ProfileImagePolicy
from arttrip.application.domain.user.user import User
from arttrip.application.util.exception import DomainException

KST = timezone(timedelta(hours=9))

UTC_NOW = datetime(2026, 9, 15, 12, 0, tzinfo=UTC)
KST_NOW = datetime(2026, 9, 15, 21, 0, tzinfo=KST)
NAIVE_NOW = datetime(2026, 9, 15, 12, 0)
DEFAULT_IMAGE = ProfileImagePolicy(default_key="defaults/profile.jpg")


def _user() -> User:
    return User.register(
        provider_name="tester", email=None, now=UTC_NOW, image_policy=DEFAULT_IMAGE
    )


class TestSocialAccount:
    @pytest.mark.parametrize("provider_user_id", ["", "   "])
    def test_공급자_식별자가_공백일경우_예외(self, provider_user_id: str) -> None:
        # given
        user = _user()

        # when
        # then
        with pytest.raises(DomainException) as exc_info:
            user.link_social(
                provider=SocialProvider.GOOGLE,
                provider_user_id=provider_user_id,
                now=UTC_NOW,
            )
        assert exc_info.value.code == "SOCIAL_ACCOUNT_PROVIDER_USER_ID_BLANK"

    def test_연결시각이_naive이면_예외(self) -> None:
        # given
        user = _user()

        # when
        # then
        with pytest.raises(DomainException) as exc_info:
            user.link_social(
                provider=SocialProvider.GOOGLE,
                provider_user_id="google-sub",
                now=NAIVE_NOW,
            )

        assert exc_info.value.code == "DATETIME_NAIVE"

    def test_KST로_들어온_시각은_UTC로_변환해_저장한다(self) -> None:
        # given
        user = _user()

        # when
        user.link_social(
            provider=SocialProvider.KAKAO,
            provider_user_id="kakao-sub",
            now=KST_NOW,
        )

        # then
        account = user.social_accounts[0]
        assert account.linked_at == UTC_NOW
        assert account.linked_at.utcoffset() == timedelta(0)

    def test_같은_공급자를_두_번_연결하면_예외(self) -> None:
        # given
        user = _user()
        user.link_social(
            provider=SocialProvider.KAKAO, provider_user_id="kakao-1", now=UTC_NOW
        )

        # when
        # then
        with pytest.raises(DomainException) as exc_info:
            user.link_social(
                provider=SocialProvider.KAKAO, provider_user_id="kakao-2", now=UTC_NOW
            )
        assert exc_info.value.code == "USER_PROVIDER_ALREADY_LINKED"
