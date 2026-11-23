from fastapi import Request

from arttrip.application.domain.user.user_services import (
    ChangeNicknameService,
    ChangeProfileImageService,
    ChangePushEnabledService,
    CompleteOnboardingKeywordsService,
    CompleteOnboardingNicknameService,
    GetProfileService,
    ListMyKeywordsService,
    RegisterDeviceTokenService,
    RemoveProfileImageService,
    ReplaceKeywordsService,
    SelectOnboardingRoleService,
)
from arttrip.application.port.input.user.use_cases import (
    ChangeNicknameUseCase,
    ChangeProfileImageUseCase,
    ChangePushEnabledUseCase,
    CompleteOnboardingKeywordsUseCase,
    CompleteOnboardingNicknameUseCase,
    GetProfileUseCase,
    ListMyKeywordsUseCase,
    RegisterDeviceTokenUseCase,
    RemoveProfileImageUseCase,
    ReplaceKeywordsUseCase,
    SelectOnboardingRoleUseCase,
)
from arttrip.bootstrap.wiring.common import Overrides, new_unit_of_work
from arttrip.inbound.http.dependencies.user import (
    provide_change_nickname_use_case,
    provide_change_profile_image_use_case,
    provide_change_push_enabled_use_case,
    provide_complete_onboarding_keywords_use_case,
    provide_complete_onboarding_nickname_use_case,
    provide_get_profile_use_case,
    provide_list_my_keywords_use_case,
    provide_register_device_token_use_case,
    provide_remove_profile_image_use_case,
    provide_replace_keywords_use_case,
    provide_select_onboarding_role_use_case,
)


def build_change_push_enabled_use_case(request: Request) -> ChangePushEnabledUseCase:
    return ChangePushEnabledService(uow=new_unit_of_work(request))


def build_register_device_token_use_case(
    request: Request,
) -> RegisterDeviceTokenUseCase:
    return RegisterDeviceTokenService(uow=new_unit_of_work(request))


def build_change_profile_image_use_case(
    request: Request,
) -> ChangeProfileImageUseCase:
    return ChangeProfileImageService(
        uow=new_unit_of_work(request),
        storage=request.app.state.image_storage,
        policy=request.app.state.profile_image_policy,
    )


def build_remove_profile_image_use_case(
    request: Request,
) -> RemoveProfileImageUseCase:
    return RemoveProfileImageService(
        uow=new_unit_of_work(request),
        storage=request.app.state.image_storage,
        policy=request.app.state.profile_policy,
    )


def build_get_profile_use_case(request: Request) -> GetProfileUseCase:
    return GetProfileService(
        uow=new_unit_of_work(request),
        storage=request.app.state.image_storage,
    )


def build_change_nickname_use_case(request: Request) -> ChangeNicknameUseCase:
    return ChangeNicknameService(uow=new_unit_of_work(request))


def build_select_onboarding_role_use_case(
    request: Request,
) -> SelectOnboardingRoleUseCase:
    return SelectOnboardingRoleService(uow=new_unit_of_work(request))


def build_replace_keywords_use_case(request: Request) -> ReplaceKeywordsUseCase:
    return ReplaceKeywordsService(uow=new_unit_of_work(request))


def build_list_my_keywords_use_case(request: Request) -> ListMyKeywordsUseCase:
    return ListMyKeywordsService(uow=new_unit_of_work(request))


def build_complete_onboarding_nickname_use_case(
    request: Request,
) -> CompleteOnboardingNicknameUseCase:
    return CompleteOnboardingNicknameService(uow=new_unit_of_work(request))


def build_complete_onboarding_keywords_use_case(
    request: Request,
) -> CompleteOnboardingKeywordsUseCase:
    return CompleteOnboardingKeywordsService(uow=new_unit_of_work(request))


def wire_user(overrides: Overrides) -> None:
    overrides[provide_change_push_enabled_use_case] = build_change_push_enabled_use_case
    overrides[provide_register_device_token_use_case] = (
        build_register_device_token_use_case
    )
    overrides[provide_get_profile_use_case] = build_get_profile_use_case
    overrides[provide_change_nickname_use_case] = build_change_nickname_use_case
    overrides[provide_select_onboarding_role_use_case] = (
        build_select_onboarding_role_use_case
    )
    overrides[provide_replace_keywords_use_case] = build_replace_keywords_use_case
    overrides[provide_list_my_keywords_use_case] = build_list_my_keywords_use_case
    overrides[provide_change_profile_image_use_case] = (
        build_change_profile_image_use_case
    )
    overrides[provide_remove_profile_image_use_case] = (
        build_remove_profile_image_use_case
    )
    overrides[provide_complete_onboarding_nickname_use_case] = (
        build_complete_onboarding_nickname_use_case
    )
    overrides[provide_complete_onboarding_keywords_use_case] = (
        build_complete_onboarding_keywords_use_case
    )
