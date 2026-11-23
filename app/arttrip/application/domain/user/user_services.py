import logging
from datetime import UTC, datetime
from typing import Final

from arttrip.application.domain.image.exceptions import ImageError
from arttrip.application.domain.image.image_key import new_image_key
from arttrip.application.domain.keyword.exceptions import KeywordError
from arttrip.application.domain.keyword.keyword import Keyword
from arttrip.application.domain.keyword.keyword_services import to_keyword_view
from arttrip.application.domain.user.current_user import load_current_user
from arttrip.application.domain.user.exceptions import UserError
from arttrip.application.domain.user.nickname import validate_nickname
from arttrip.application.domain.user.profile_image_policy import ProfileImagePolicy
from arttrip.application.port.input.keyword.results import KeywordView
from arttrip.application.port.input.user.commands import (
    ChangeNicknameCommand,
    ChangeProfileImageCommand,
    ChangePushEnabledCommand,
    CompleteOnboardingKeywordsCommand,
    CompleteOnboardingNicknameCommand,
    DeleteAccountCommand,
    RegisterDeviceTokenCommand,
    ReplaceKeywordsCommand,
    SelectOnboardingRoleCommand,
)
from arttrip.application.port.input.user.results import (
    ChangeNicknameResult,
    OnboardingProgress,
    ProfileImage,
    ReplaceKeywordsResult,
    UserProfile,
)
from arttrip.application.port.input.user.use_cases import (
    ChangeNicknameUseCase,
    ChangeProfileImageUseCase,
    ChangePushEnabledUseCase,
    CompleteOnboardingKeywordsUseCase,
    CompleteOnboardingNicknameUseCase,
    DeleteAccountUseCase,
    GetProfileUseCase,
    ListMyKeywordsUseCase,
    RegisterDeviceTokenUseCase,
    RemoveProfileImageUseCase,
    ReplaceKeywordsUseCase,
    SelectOnboardingRoleUseCase,
)
from arttrip.application.port.output.access_token_denylist_port import (
    AccessTokenDenylistPort,
)
from arttrip.application.port.output.image_storage_port import ImageStoragePort
from arttrip.application.port.output.refresh_token_port import RefreshTokenPort
from arttrip.application.port.output.unit_of_work import UnitOfWork

_logger = logging.getLogger(__name__)
PROFILE_IMAGE_FOLDER: Final = "profiles"


class GetProfileService(GetProfileUseCase):
    def __init__(self, *, uow: UnitOfWork, storage: ImageStoragePort) -> None:
        self._uow = uow
        self._storage = storage

    def get_profile(self, user_id: int) -> UserProfile:
        with self._uow as uow:
            user = load_current_user(uow.users, user_id)
            return UserProfile(
                nickname=user.nickname,
                email=user.email,
                role=user.role,
                onboarding_step=user.onboarding_step,
                push_enabled=user.push_enabled,
                profile_image_url=self._storage.public_url(user.profile_image_key),
            )


class ChangeNicknameService(ChangeNicknameUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def change_nickname(self, command: ChangeNicknameCommand) -> ChangeNicknameResult:
        nickname = validate_nickname(command.nickname)

        with self._uow as uow:
            user = load_current_user(uow.users, command.user_id)
            if uow.users.is_nickname_taken(
                nickname=nickname, except_user_id=command.user_id
            ):
                raise UserError.duplicated_nickname()

            user.change_nickname(nickname=nickname, now=datetime.now(UTC))
            return ChangeNicknameResult(
                nickname=user.nickname, onboarding_step=user.onboarding_step
            )


class CompleteOnboardingNicknameService(CompleteOnboardingNicknameUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def complete_onboarding_nickname(
        self, command: CompleteOnboardingNicknameCommand
    ) -> ChangeNicknameResult:
        nickname = (
            None if command.nickname is None else validate_nickname(command.nickname)
        )

        with self._uow as uow:
            user = load_current_user(uow.users, command.user_id)
            # 닉네임을 직접 입력했을 때만 중복을 검사한다
            if nickname is not None and uow.users.is_nickname_taken(
                nickname=nickname, except_user_id=command.user_id
            ):
                raise UserError.duplicated_nickname()

            user.complete_nickname_step(nickname=nickname, now=datetime.now(UTC))
            return ChangeNicknameResult(
                nickname=user.nickname, onboarding_step=user.onboarding_step
            )


class SelectOnboardingRoleService(SelectOnboardingRoleUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def select_onboarding_role(
        self, command: SelectOnboardingRoleCommand
    ) -> OnboardingProgress:
        with self._uow as uow:
            user = load_current_user(uow.users, command.user_id)
            user.select_role(desired_role=command.desired_role, now=datetime.now(UTC))
            return OnboardingProgress(
                onboarding_step=user.onboarding_step, role=user.role
            )


class ReplaceKeywordsService(ReplaceKeywordsUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def replace_keywords(
        self, command: ReplaceKeywordsCommand
    ) -> ReplaceKeywordsResult:
        with self._uow as uow:
            user = load_current_user(uow.users, command.user_id)
            keywords = _find_requested_keywords(uow, command.keyword_ids)
            user.replace_keywords(keywords=keywords, now=datetime.now(UTC))
            saved_ids = tuple(sorted(k.keyword_id for k in user.keywords))
            return ReplaceKeywordsResult(
                keyword_ids=saved_ids, onboarding_step=user.onboarding_step
            )


class CompleteOnboardingKeywordsService(CompleteOnboardingKeywordsUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def complete_onboarding_keywords(
        self, command: CompleteOnboardingKeywordsCommand
    ) -> ReplaceKeywordsResult:
        with self._uow as uow:
            user = load_current_user(uow.users, command.user_id)
            keywords = _find_requested_keywords(uow, command.keyword_ids)
            user.complete_keyword_step(keywords=keywords, now=datetime.now(UTC))
            saved_ids = tuple(sorted(k.keyword_id for k in user.keywords))
            return ReplaceKeywordsResult(
                keyword_ids=saved_ids, onboarding_step=user.onboarding_step
            )


def _find_requested_keywords(
    uow: UnitOfWork, keyword_ids: tuple[int, ...]
) -> list[Keyword]:
    requested_ids = set(keyword_ids)
    keywords = uow.keywords.find_by_ids(requested_ids)
    # 없는 id 가 섞이면 일부만 저장하지 않고 거부한다
    if len(keywords) != len(requested_ids):
        raise KeywordError.not_found()
    return keywords


class ListMyKeywordsService(ListMyKeywordsUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def list_my_keywords(self, user_id: int) -> list[KeywordView]:
        with self._uow as uow:
            user = load_current_user(uow.users, user_id)
            keywords = uow.keywords.find_by_ids({k.keyword_id for k in user.keywords})
            ordered = sorted(keywords, key=lambda k: (k.keyword_type, k.id or 0))
            return [to_keyword_view(keyword) for keyword in ordered]


class ChangePushEnabledService(ChangePushEnabledUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def change_push_enabled(self, command: ChangePushEnabledCommand) -> bool:
        with self._uow as uow:
            user = load_current_user(uow.users, command.user_id)
            user.change_push_enabled(enabled=command.enabled, now=datetime.now(UTC))
            return user.push_enabled


class RegisterDeviceTokenService(RegisterDeviceTokenUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def register_device_token(self, command: RegisterDeviceTokenCommand) -> None:
        with self._uow as uow:
            load_current_user(uow.users, command.user_id)
            uow.device_tokens.assign_to_user(
                user_id=command.user_id, token=command.token
            )


class ChangeProfileImageService(ChangeProfileImageUseCase):
    def __init__(
        self, *, uow: UnitOfWork, storage: ImageStoragePort, policy: ProfileImagePolicy
    ) -> None:
        self._uow = uow
        self._storage = storage
        self._policy = policy

    def change_profile_image(self, command: ChangeProfileImageCommand) -> ProfileImage:
        key = new_image_key(folder=PROFILE_IMAGE_FOLDER, extension=command.extension)
        self._storage.upload(
            key=key, content=command.content, content_type=command.content_type
        )
        try:
            with self._uow as uow:
                user = load_current_user(uow.users, command.user_id)
                previous_key = user.change_profile_image(
                    key=key, policy=self._policy, now=datetime.now(UTC)
                )
        except Exception:
            _delete_quietly(self._storage, key)
            raise
        if previous_key is not None:
            _delete_quietly(self._storage, previous_key)
        return ProfileImage(url=self._storage.public_url(key))


class RemoveProfileImageService(RemoveProfileImageUseCase):
    def __init__(
        self, *, uow: UnitOfWork, storage: ImageStoragePort, policy: ProfileImagePolicy
    ) -> None:
        self._uow = uow
        self._storage = storage
        self._policy = policy

    def remove_profile_image(self, user_id: int) -> None:
        with self._uow as uow:
            user = load_current_user(uow.users, user_id)
            previous_key = user.remove_profile_image(
                now=datetime.now(UTC), policy=self._policy
            )
        if previous_key is not None:
            _delete_quietly(self._storage, previous_key)


def _delete_quietly(storage: ImageStoragePort, key: str) -> None:
    try:
        storage.delete(key)
    except ImageError:
        _logger.exception("stored image could not be deleted: %s", key)


class DeleteAccountService(DeleteAccountUseCase):
    def __init__(
        self,
        *,
        uow: UnitOfWork,
        refresh_tokens: RefreshTokenPort,
        access_token_denylist: AccessTokenDenylistPort,
    ) -> None:
        self._uow = uow
        self._refresh_tokens = refresh_tokens
        self._access_token_denylist = access_token_denylist

    def delete_account(self, command: DeleteAccountCommand) -> None:
        with self._uow as uow:
            user = load_current_user(uow.users, command.user_id)

            user.ensure_can_delete_account()
            for exhibit_id in uow.exhibits.find_ids_by_owner(command.user_id):
                uow.exhibits.remove_with_dependents(exhibit_id)

            uow.users.remove_with_owned_data(command.user_id)

        self._refresh_tokens.consume(command.refresh_token)
        self._access_token_denylist.deny(
            token_id=command.access_token_id,
            expires_at=command.access_token_expires_at,
        )
