from collections.abc import Sequence
from datetime import datetime

from arttrip.application.domain.auth.exceptions import AuthError
from arttrip.application.domain.auth.social_provider import SocialProvider
from arttrip.application.domain.keyword.keyword import Keyword
from arttrip.application.domain.keyword.keyword_type import KeywordType
from arttrip.application.domain.social_account.social_account import SocialAccount
from arttrip.application.domain.user.display_name import generate_display_name
from arttrip.application.domain.user.exceptions import UserError
from arttrip.application.domain.user.nickname import (
    is_valid_nickname,
    validate_nickname,
)
from arttrip.application.domain.user.onboarding_step import OnboardingStep
from arttrip.application.domain.user.profile_image_policy import ProfileImagePolicy
from arttrip.application.domain.user.role import UserRole
from arttrip.application.domain.user.user_keyword import UserKeyword
from arttrip.application.util.utc import to_utc


class User:
    def __init__(
        self,
        *,
        id_: int | None,
        nickname: str,
        email: str | None,
        role: UserRole,
        onboarding_step: OnboardingStep,
        push_enabled: bool,
        registered_at: datetime,
        updated_at: datetime,
        profile_image_key: str,
    ) -> None:
        if not nickname.strip():
            raise UserError.blank_nickname()
        self._id = id_
        self.nickname = nickname
        self.email = email
        self.role = role
        self.onboarding_step = onboarding_step
        self.push_enabled = push_enabled
        self.registered_at = to_utc(registered_at)
        self.updated_at = to_utc(updated_at)
        self.social_accounts: list[SocialAccount] = []
        self.keywords: list[UserKeyword] = []
        self.profile_image_key = profile_image_key

    @property
    def id(self) -> int | None:
        return self._id

    @classmethod
    def register(
        cls,
        *,
        provider_name: str | None,
        email: str | None,
        now: datetime,
        image_policy: ProfileImagePolicy,
    ) -> "User":
        candidate = provider_name.strip() if provider_name else ""
        nickname = (
            candidate if is_valid_nickname(candidate) else generate_display_name()
        )
        return cls(
            id_=None,
            nickname=nickname,
            email=email,
            role=UserRole.USER,
            onboarding_step=OnboardingStep.NICKNAME,
            push_enabled=False,
            registered_at=now,
            updated_at=now,
            profile_image_key=image_policy.default_key,
        )

    def link_social(
        self, *, provider: SocialProvider, provider_user_id: str, now: datetime
    ) -> None:
        if any(a.provider == provider for a in self.social_accounts):
            raise UserError.provider_already_linked()
        self.social_accounts.append(
            SocialAccount(
                id_=None,
                provider=provider,
                provider_user_id=provider_user_id,
                linked_at=now,
            )
        )

    def select_role(self, *, desired_role: UserRole, now: datetime) -> None:
        if self.onboarding_step is OnboardingStep.NICKNAME:
            raise UserError.role_step_not_reached()

        if self.onboarding_step is not OnboardingStep.ROLE_SELECTION:
            raise UserError.role_already_selected()

        if desired_role not in (UserRole.USER, UserRole.ARTIST):
            raise UserError.role_not_selectable()

        self.onboarding_step = (
            OnboardingStep.ARTIST_VERIFICATION
            if desired_role is UserRole.ARTIST
            else OnboardingStep.KEYWORD
        )
        self._touch(now)

    def change_nickname(self, *, nickname: str, now: datetime) -> None:
        # 마이페이지 변경. 온보딩 단계는 바꾸지 않는다
        self.nickname = validate_nickname(nickname)
        self._touch(now)

    def complete_nickname_step(self, *, nickname: str | None, now: datetime) -> None:
        if self.onboarding_step is not OnboardingStep.NICKNAME:
            raise UserError.nickname_step_already_completed()
        # None 이면 가입 때 정한 기본 닉네임을 그대로 확정한다
        if nickname is not None:
            self.nickname = validate_nickname(nickname)
        self.onboarding_step = OnboardingStep.ROLE_SELECTION
        self._touch(now)

    def change_profile_image(
        self, *, key: str, policy: ProfileImagePolicy, now: datetime
    ) -> str | None:
        previous_key = self.profile_image_key
        self.profile_image_key = key
        self._touch(now)
        return None if policy.is_default(previous_key) else previous_key

    def remove_profile_image(
        self, *, policy: ProfileImagePolicy, now: datetime
    ) -> str | None:
        previous_key = self.profile_image_key
        if policy.is_default(previous_key):
            return None
        self.profile_image_key = policy.default_key
        self._touch(now)
        return previous_key

    def replace_keywords(self, *, keywords: Sequence[Keyword], now: datetime) -> None:
        if self.onboarding_step not in (
            OnboardingStep.KEYWORD,
            OnboardingStep.COMPLETED,
        ):
            raise UserError.keyword_step_not_reached()
        if not any(k.keyword_type is KeywordType.GENRE for k in keywords):
            raise UserError.genre_keyword_required()

        selected_ids = {k.id for k in keywords if k.id is not None}

        removed = [k for k in self.keywords if k.keyword_id not in selected_ids]
        for user_keyword in removed:
            self.keywords.remove(user_keyword)

        kept_ids = {k.keyword_id for k in self.keywords}
        for keyword_id in sorted(selected_ids - kept_ids):
            self.keywords.append(
                UserKeyword(id_=None, keyword_id=keyword_id, selected_at=now)
            )

        self._touch(now)

    def complete_keyword_step(
        self, *, keywords: Sequence[Keyword], now: datetime
    ) -> None:
        if self.onboarding_step is OnboardingStep.COMPLETED:
            raise UserError.keyword_step_already_completed()
        if self.onboarding_step is not OnboardingStep.KEYWORD:
            raise UserError.keyword_step_not_reached()
        # 키워드 저장 규칙(장르 필수 등)은 replace_keywords 한 곳에 둔다
        self.replace_keywords(keywords=keywords, now=now)
        self.onboarding_step = OnboardingStep.COMPLETED

    def change_push_enabled(self, *, enabled: bool, now: datetime) -> None:
        self.push_enabled = enabled
        self._touch(now)

    def request_artist_verification(self, *, now: datetime) -> None:
        if self.role is not UserRole.USER:
            raise UserError.artist_verification_not_allowed()
        if self.onboarding_step is OnboardingStep.ARTIST_VERIFICATION:
            self.onboarding_step = OnboardingStep.KEYWORD
        self._touch(now)

    def become_artist(self, *, now: datetime) -> None:
        if self.role is not UserRole.USER:
            raise UserError.artist_verification_not_allowed()
        self.role = UserRole.ARTIST
        self._touch(now)

    def ensure_artist(self) -> None:
        if self.role is not UserRole.ARTIST:
            raise UserError.artist_role_required()

    def _touch(self, now: datetime) -> None:
        self.updated_at = to_utc(now)

    def ensure_can_delete_account(self) -> None:
        if self.role is UserRole.ADMIN:
            raise UserError.admin_cannot_delete_account()

    def ensure_can_sign_in_web(self) -> None:
        if self.role is not UserRole.ADMIN:
            raise AuthError.web_sign_in_not_allowed()
