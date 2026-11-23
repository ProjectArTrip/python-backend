from datetime import UTC, datetime

import pytest
from arttrip.application.domain.keyword.keyword import Keyword
from arttrip.application.domain.keyword.keyword_type import KeywordType
from arttrip.application.domain.user.onboarding_step import OnboardingStep
from arttrip.application.domain.user.profile_image_policy import ProfileImagePolicy
from arttrip.application.domain.user.role import UserRole
from arttrip.application.domain.user.user import User
from arttrip.application.util.exception import DomainException

NOW = datetime(2026, 9, 13, 12, 0, tzinfo=UTC)
NAIVE_NOW = datetime(2026, 9, 13, 12, 0)


LATER = datetime(2026, 9, 14, 12, 0, tzinfo=UTC)

GENRE = Keyword(id_=1, name="회화", keyword_type=KeywordType.GENRE)
OTHER_GENRE = Keyword(id_=2, name="조각", keyword_type=KeywordType.GENRE)
STYLE = Keyword(id_=12, name="몰입형", keyword_type=KeywordType.STYLE)
DEFAULT_IMAGE = ProfileImagePolicy(default_key="defaults/profile.jpg")


def user_with(*, role: UserRole, step: OnboardingStep) -> User:
    return User(
        id_=1,
        nickname="아트트립",
        email=None,
        role=role,
        onboarding_step=step,
        push_enabled=False,
        registered_at=NOW,
        updated_at=NOW,
        profile_image_key=DEFAULT_IMAGE.default_key,
    )


class TestUserRegistration:
    def test_가입은_항상_일반사용자다(self) -> None:
        # given
        # when
        user = User.register(
            provider_name=None, email=None, now=NOW, image_policy=DEFAULT_IMAGE
        )

        # then
        assert user.role is UserRole.USER

    def test_가입시_푸시는_꺼져있다(self) -> None:
        # given
        # when
        user = User.register(
            provider_name=None, email=None, now=NOW, image_policy=DEFAULT_IMAGE
        )

        # then
        assert user.push_enabled is False

    @pytest.mark.parametrize("provider_name", [None, "", "   "])
    def test_공급자_이름이_없거나_공백이면_닉네임을_생성한다(
        self, provider_name: str | None
    ) -> None:
        # given
        # when
        user = User.register(
            provider_name=provider_name, email=None, now=NOW, image_policy=DEFAULT_IMAGE
        )

        # then
        assert user.nickname.strip()
        assert user.onboarding_step is OnboardingStep.NICKNAME

    @pytest.mark.parametrize("nickname", ["", "   "])
    def test_닉네임이_공백이면_예외(self, nickname: str) -> None:
        # given
        # when

        # then
        with pytest.raises(DomainException) as exc_info:
            User(
                id_=None,
                nickname=nickname,
                email=None,
                role=UserRole.USER,
                onboarding_step=OnboardingStep.ROLE_SELECTION,
                push_enabled=False,
                registered_at=NOW,
                updated_at=NOW,
                profile_image_key=DEFAULT_IMAGE.default_key,
            )
        assert exc_info.value.code == "USER_NICKNAME_BLANK"

    def test_가입시각이_naive면_예외(self) -> None:
        # given
        # when

        # then
        with pytest.raises(DomainException) as exc_info:
            User.register(
                provider_name=None,
                email=None,
                now=NAIVE_NOW,
                image_policy=DEFAULT_IMAGE,
            )
        assert exc_info.value.code == "DATETIME_NAIVE"


class TestOnboardingRole:
    @pytest.mark.parametrize("desired_role", [UserRole.USER, UserRole.ARTIST])
    def test_닉네임_단계에서는_권한을_고를_수_없다(
        self, desired_role: UserRole
    ) -> None:
        # given
        user = User.register(
            provider_name=None, email=None, now=NOW, image_policy=DEFAULT_IMAGE
        )

        # when
        # then
        with pytest.raises(DomainException) as exc_info:
            user.select_role(desired_role=desired_role, now=NOW)
        assert exc_info.value.code == "USER_ROLE_STEP_NOT_REACHED"
        assert user.onboarding_step is OnboardingStep.NICKNAME

    def test_관리자_역할은_선택할_수_없다(self) -> None:
        # given
        user = user_with(role=UserRole.USER, step=OnboardingStep.ROLE_SELECTION)

        # when
        # then
        with pytest.raises(DomainException) as exc_info:
            user.select_role(desired_role=UserRole.ADMIN, now=NOW)
        assert exc_info.value.code == "USER_ROLE_NOT_SELECTABLE"
        assert user.role is UserRole.USER
        assert user.onboarding_step is OnboardingStep.ROLE_SELECTION

    def test_아티스트를_선택해도_권한은_일반사용자다(self) -> None:
        # given
        user = user_with(role=UserRole.USER, step=OnboardingStep.ROLE_SELECTION)

        # when
        user.select_role(desired_role=UserRole.ARTIST, now=NOW)

        # then
        assert user.role is UserRole.USER
        assert user.onboarding_step is OnboardingStep.ARTIST_VERIFICATION

    @pytest.mark.parametrize("desired_role", [UserRole.USER, UserRole.ARTIST])
    def test_role_선택은_두_번_불가능(self, desired_role: UserRole) -> None:
        # given
        user = user_with(role=UserRole.USER, step=OnboardingStep.ROLE_SELECTION)
        user.select_role(desired_role=UserRole.USER, now=NOW)

        # when
        # then
        with pytest.raises(DomainException) as exc_info:
            user.select_role(desired_role=desired_role, now=NOW)
        assert exc_info.value.code == "USER_ROLE_ALREADY_SELECTED"
        assert user.onboarding_step is OnboardingStep.KEYWORD


class TestNickname:
    @pytest.mark.parametrize(
        "nickname",
        [
            "",
            "   ",
            "a",
            "가" * 11,
            "ab cd",
            "닉네임!",
            "ㄱㄴ",
            "ab\ncd",
            "１２３",
            "<b>",
        ],
    )
    def test_규칙에_맞지_않는_닉네임은_거부하고_상태를_바꾸지_않는다(
        self, nickname: str
    ) -> None:
        # given
        user = User.register(
            provider_name="기존이름", email=None, now=NOW, image_policy=DEFAULT_IMAGE
        )

        # when
        # then
        with pytest.raises(DomainException) as exc_info:
            user.change_nickname(nickname=nickname, now=NOW)
        assert exc_info.value.code == "USER_NICKNAME_INVALID"
        assert user.nickname == "기존이름"
        assert user.onboarding_step is OnboardingStep.NICKNAME

    @pytest.mark.parametrize("nickname", ["가나", "가" * 10])
    def test_길이_경계의_닉네임은_허용한다(self, nickname: str) -> None:
        # given
        user = User.register(
            provider_name=None, email=None, now=NOW, image_policy=DEFAULT_IMAGE
        )

        # when
        user.complete_nickname_step(nickname=nickname, now=NOW)

        # then
        assert user.nickname == nickname
        assert user.onboarding_step is OnboardingStep.ROLE_SELECTION

    def test_온보딩을_마친_뒤_닉네임을_바꿔도_단계는_그대로다(self) -> None:
        # given
        user = User(
            id_=1,
            nickname="기존이름",
            email=None,
            role=UserRole.USER,
            onboarding_step=OnboardingStep.COMPLETED,
            push_enabled=False,
            registered_at=NOW,
            updated_at=NOW,
            profile_image_key=DEFAULT_IMAGE.default_key,
        )

        # when
        user.change_nickname(nickname="새이름", now=NOW)

        # then
        assert user.onboarding_step is OnboardingStep.COMPLETED

    # 막는 실패: 닉네임 단계를 지난 뒤 온보딩 닉네임 재호출 (금지된 상태 전이)
    @pytest.mark.parametrize(
        "step", [OnboardingStep.ROLE_SELECTION, OnboardingStep.COMPLETED]
    )
    def test_닉네임_단계가_아니면_온보딩_닉네임을_완료할_수_없다(
        self, step: OnboardingStep
    ) -> None:
        # given
        user = user_with(role=UserRole.USER, step=step)

        # when
        with pytest.raises(DomainException) as raised:
            user.complete_nickname_step(nickname="새이름", now=LATER)

        # then
        assert raised.value.code == "USER_NICKNAME_STEP_ALREADY_COMPLETED"
        assert user.nickname == "아트트립"
        assert user.onboarding_step is step


class TestKeywords:
    @pytest.mark.parametrize(
        "step",
        [
            OnboardingStep.ROLE_SELECTION,
            OnboardingStep.ARTIST_VERIFICATION,
            OnboardingStep.NICKNAME,
        ],
    )
    def test_키워드_단계_전에는_저장할_수_없다(self, step: OnboardingStep) -> None:
        # given
        user = user_with(role=UserRole.USER, step=step)

        # when
        with pytest.raises(DomainException) as raised:
            user.replace_keywords(keywords=[GENRE], now=LATER)

        # then
        assert raised.value.code == "USER_KEYWORD_STEP_NOT_REACHED"
        assert user.onboarding_step is step
        assert user.keywords == []

    def test_장르가_없으면_저장할_수_없다(self) -> None:
        # given
        user = user_with(role=UserRole.USER, step=OnboardingStep.KEYWORD)

        # when
        with pytest.raises(DomainException) as raised:
            user.replace_keywords(keywords=[STYLE], now=LATER)

        # then
        assert raised.value.code == "USER_GENRE_KEYWORD_REQUIRED"
        assert user.onboarding_step is OnboardingStep.KEYWORD
        assert user.keywords == []

    def test_교체가_거부되면_기존_선택이_그대로다(self) -> None:
        # given
        user = user_with(role=UserRole.USER, step=OnboardingStep.KEYWORD)
        user.replace_keywords(keywords=[GENRE, STYLE], now=NOW)

        # when
        with pytest.raises(DomainException):
            user.replace_keywords(keywords=[STYLE], now=LATER)

        # then
        assert sorted(k.keyword_id for k in user.keywords) == [1, 12]

    def test_다시_고른_키워드는_기존_항목을_유지한다(self) -> None:
        # given
        user = user_with(role=UserRole.USER, step=OnboardingStep.KEYWORD)
        user.replace_keywords(keywords=[GENRE, STYLE], now=NOW)
        kept = next(k for k in user.keywords if k.keyword_id == 1)

        # when
        user.replace_keywords(keywords=[GENRE, OTHER_GENRE], now=LATER)

        # then
        assert sorted(k.keyword_id for k in user.keywords) == [1, 2]
        assert next(k for k in user.keywords if k.keyword_id == 1) is kept
        assert kept.selected_at == NOW

    def test_같은_요청을_반복해도_중복되지_않는다(self) -> None:
        # given
        user = user_with(role=UserRole.USER, step=OnboardingStep.KEYWORD)
        user.replace_keywords(keywords=[GENRE, GENRE, STYLE], now=NOW)

        # when
        user.replace_keywords(keywords=[GENRE, STYLE], now=LATER)

        # then
        assert sorted(k.keyword_id for k in user.keywords) == [1, 12]
        assert user.onboarding_step is OnboardingStep.KEYWORD

    # 막는 실패: 키워드 단계 밖에서 온보딩 완료 시도 (금지된 상태 전이)
    @pytest.mark.parametrize(
        ("step", "code"),
        [
            (OnboardingStep.NICKNAME, "USER_KEYWORD_STEP_NOT_REACHED"),
            (OnboardingStep.ROLE_SELECTION, "USER_KEYWORD_STEP_NOT_REACHED"),
            (OnboardingStep.ARTIST_VERIFICATION, "USER_KEYWORD_STEP_NOT_REACHED"),
            (OnboardingStep.COMPLETED, "USER_KEYWORD_STEP_ALREADY_COMPLETED"),
        ],
    )
    def test_키워드_단계가_아니면_온보딩_키워드를_완료할_수_없다(
        self, step: OnboardingStep, code: str
    ) -> None:
        # given
        user = user_with(role=UserRole.USER, step=step)

        # when
        with pytest.raises(DomainException) as raised:
            user.complete_keyword_step(keywords=[GENRE], now=LATER)

        # then
        assert raised.value.code == code
        assert user.onboarding_step is step
        assert user.keywords == []

    # 막는 실패: 장르 없이 온보딩을 끝낸 사용자 생성
    def test_장르가_없으면_온보딩_키워드를_완료할_수_없다(self) -> None:
        # given
        user = user_with(role=UserRole.USER, step=OnboardingStep.KEYWORD)

        # when
        with pytest.raises(DomainException) as raised:
            user.complete_keyword_step(keywords=[STYLE], now=LATER)

        # then
        assert raised.value.code == "USER_GENRE_KEYWORD_REQUIRED"
        assert user.onboarding_step is OnboardingStep.KEYWORD
        assert user.keywords == []


class TestArtistRole:
    @pytest.mark.parametrize("role", [UserRole.ARTIST, UserRole.ADMIN])
    def test_일반_사용자가_아니면_신청할_수_없다(self, role: UserRole) -> None:
        # given
        user = user_with(role=role, step=OnboardingStep.COMPLETED)

        # when
        with pytest.raises(DomainException) as raised:
            user.request_artist_verification(now=LATER)

        # then
        assert raised.value.code == "USER_ARTIST_VERIFICATION_NOT_ALLOWED"
        assert user.role is role

    def test_신청해도_역할은_일반_사용자_그대로다(self) -> None:
        # given
        user = user_with(role=UserRole.USER, step=OnboardingStep.ARTIST_VERIFICATION)

        # when
        user.request_artist_verification(now=LATER)

        # then
        assert user.role is UserRole.USER
        assert user.onboarding_step is OnboardingStep.KEYWORD

    @pytest.mark.parametrize("step", [OnboardingStep.KEYWORD, OnboardingStep.COMPLETED])
    def test_인증_단계가_아니면_온보딩_단계를_바꾸지_않는다(
        self, step: OnboardingStep
    ) -> None:
        # given
        user = user_with(role=UserRole.USER, step=step)

        # when
        user.request_artist_verification(now=LATER)

        # then
        assert user.onboarding_step is step

    @pytest.mark.parametrize("role", [UserRole.ADMIN, UserRole.ARTIST])
    def test_일반_사용자가_아니면_아티스트로_바꿀_수_없다(self, role: UserRole) -> None:
        # given
        user = user_with(role=role, step=OnboardingStep.COMPLETED)

        # when
        with pytest.raises(DomainException) as raised:
            user.become_artist(now=LATER)

        # then
        assert raised.value.code == "USER_ARTIST_VERIFICATION_NOT_ALLOWED"
        assert user.role is role
        assert user.updated_at == NOW

    def test_승인_전_사용자는_아티스트가_아니다(self) -> None:
        # given
        applicant = user_with(
            role=UserRole.USER, step=OnboardingStep.ARTIST_VERIFICATION
        )

        # when
        with pytest.raises(DomainException) as raised:
            applicant.ensure_artist()

        # then
        assert raised.value.code == "USER_ARTIST_ROLE_REQUIRED"


class TestAccessRestrictions:
    def test_관리자는_탈퇴할_수_없다(self) -> None:
        # given
        admin = user_with(role=UserRole.ADMIN, step=OnboardingStep.COMPLETED)

        # when
        with pytest.raises(DomainException) as raised:
            admin.ensure_can_delete_account()

        # then
        assert raised.value.code == "USER_ADMIN_ACCOUNT_DELETION_NOT_ALLOWED"

    @pytest.mark.parametrize("role", [UserRole.USER, UserRole.ARTIST])
    def test_관리자가_아니면_웹에_로그인할_수_없다(self, role: UserRole) -> None:
        # given
        user = user_with(role=role, step=OnboardingStep.COMPLETED)

        # when
        with pytest.raises(DomainException) as raised:
            user.ensure_can_sign_in_web()

        # then
        assert raised.value.code == "AUTH_WEB_SIGN_IN_NOT_ALLOWED"


class TestProfileImage:
    def test_프로필_이미지를_바꾸면_지워야_할_옛_키를_돌려준다(self) -> None:
        # given
        user = user_with(role=UserRole.USER, step=OnboardingStep.COMPLETED)
        user.change_profile_image(
            key="profiles/old.jpg",
            now=NOW,
            policy=DEFAULT_IMAGE,
        )

        # when
        previous_key = user.change_profile_image(
            key="profiles/new.jpg",
            now=NOW,
            policy=DEFAULT_IMAGE,
        )

        # then
        assert previous_key == "profiles/old.jpg"
        assert user.profile_image_key == "profiles/new.jpg"

    def test_기본_이미지에서_사진을_올려도_기본_이미지는_지울_대상이_아니다(
        self,
    ) -> None:
        # given
        user = user_with(role=UserRole.USER, step=OnboardingStep.COMPLETED)

        # when
        previous_key = user.change_profile_image(
            key="profiles/new.jpg", policy=DEFAULT_IMAGE, now=NOW
        )

        # then
        assert previous_key is None
        assert user.profile_image_key == "profiles/new.jpg"

    def test_기본_이미지인_사용자가_삭제해도_기본_이미지는_지우지_않는다(self) -> None:
        # given
        user = user_with(role=UserRole.USER, step=OnboardingStep.COMPLETED)

        # when
        previous_key = user.remove_profile_image(policy=DEFAULT_IMAGE, now=NOW)

        # then
        assert previous_key is None
        assert user.profile_image_key == DEFAULT_IMAGE.default_key
