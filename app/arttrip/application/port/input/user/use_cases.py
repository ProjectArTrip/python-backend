from abc import ABC, abstractmethod

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


class GetProfileUseCase(ABC):
    @abstractmethod
    def get_profile(self, user_id: int) -> UserProfile:
        pass


class ChangeNicknameUseCase(ABC):
    @abstractmethod
    def change_nickname(self, command: ChangeNicknameCommand) -> ChangeNicknameResult:
        pass


class SelectOnboardingRoleUseCase(ABC):
    @abstractmethod
    def select_onboarding_role(
        self, command: SelectOnboardingRoleCommand
    ) -> OnboardingProgress:
        pass


class CompleteOnboardingNicknameUseCase(ABC):
    @abstractmethod
    def complete_onboarding_nickname(
        self, command: CompleteOnboardingNicknameCommand
    ) -> ChangeNicknameResult:
        pass


class CompleteOnboardingKeywordsUseCase(ABC):
    @abstractmethod
    def complete_onboarding_keywords(
        self, command: CompleteOnboardingKeywordsCommand
    ) -> ReplaceKeywordsResult:
        pass


class ReplaceKeywordsUseCase(ABC):
    @abstractmethod
    def replace_keywords(
        self, command: ReplaceKeywordsCommand
    ) -> ReplaceKeywordsResult:
        pass


class ChangePushEnabledUseCase(ABC):
    @abstractmethod
    def change_push_enabled(self, command: ChangePushEnabledCommand) -> bool:
        pass


class RegisterDeviceTokenUseCase(ABC):
    @abstractmethod
    def register_device_token(self, command: RegisterDeviceTokenCommand) -> None:
        pass


class ListMyKeywordsUseCase(ABC):
    @abstractmethod
    def list_my_keywords(self, user_id: int) -> list[KeywordView]:
        pass


class ChangeProfileImageUseCase(ABC):
    @abstractmethod
    def change_profile_image(self, command: ChangeProfileImageCommand) -> ProfileImage:
        pass


class RemoveProfileImageUseCase(ABC):
    @abstractmethod
    def remove_profile_image(self, user_id: int) -> None:
        pass


class DeleteAccountUseCase(ABC):
    @abstractmethod
    def delete_account(self, command: DeleteAccountCommand) -> None:
        pass
