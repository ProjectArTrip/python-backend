from typing import Annotated

from fastapi import Depends

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


def provide_change_push_enabled_use_case() -> ChangePushEnabledUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_register_device_token_use_case() -> RegisterDeviceTokenUseCase:
    raise NotImplementedError("composition root must override this dependency")


ChangePushEnabledUseCaseDep = Annotated[
    ChangePushEnabledUseCase, Depends(provide_change_push_enabled_use_case)
]


RegisterDeviceTokenUseCaseDep = Annotated[
    RegisterDeviceTokenUseCase, Depends(provide_register_device_token_use_case)
]


def provide_get_profile_use_case() -> GetProfileUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_change_nickname_use_case() -> ChangeNicknameUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_select_onboarding_role_use_case() -> SelectOnboardingRoleUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_replace_keywords_use_case() -> ReplaceKeywordsUseCase:
    raise NotImplementedError("composition root must override this dependency")


GetProfileUseCaseDep = Annotated[
    GetProfileUseCase, Depends(provide_get_profile_use_case)
]


ChangeNicknameUseCaseDep = Annotated[
    ChangeNicknameUseCase, Depends(provide_change_nickname_use_case)
]


SelectOnboardingRoleUseCaseDep = Annotated[
    SelectOnboardingRoleUseCase, Depends(provide_select_onboarding_role_use_case)
]


ReplaceKeywordsUseCaseDep = Annotated[
    ReplaceKeywordsUseCase, Depends(provide_replace_keywords_use_case)
]


def provide_list_my_keywords_use_case() -> ListMyKeywordsUseCase:
    raise NotImplementedError("composition root must override this dependency")


ListMyKeywordsUseCaseDep = Annotated[
    ListMyKeywordsUseCase, Depends(provide_list_my_keywords_use_case)
]


def provide_change_profile_image_use_case() -> ChangeProfileImageUseCase:
    raise NotImplementedError("composition root must override this dependency")


ChangeProfileImageUseCaseDep = Annotated[
    ChangeProfileImageUseCase, Depends(provide_change_profile_image_use_case)
]


def provide_remove_profile_image_use_case() -> RemoveProfileImageUseCase:
    raise NotImplementedError("composition root must override this dependency")


RemoveProfileImageUseCaseDep = Annotated[
    RemoveProfileImageUseCase, Depends(provide_remove_profile_image_use_case)
]


def provide_complete_onboarding_nickname_use_case() -> (
    CompleteOnboardingNicknameUseCase
):
    raise NotImplementedError("composition root must override this dependency")


def provide_complete_onboarding_keywords_use_case() -> (
    CompleteOnboardingKeywordsUseCase
):
    raise NotImplementedError("composition root must override this dependency")


CompleteOnboardingNicknameUseCaseDep = Annotated[
    CompleteOnboardingNicknameUseCase,
    Depends(provide_complete_onboarding_nickname_use_case),
]


CompleteOnboardingKeywordsUseCaseDep = Annotated[
    CompleteOnboardingKeywordsUseCase,
    Depends(provide_complete_onboarding_keywords_use_case),
]
