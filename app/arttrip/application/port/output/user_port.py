from abc import ABC, abstractmethod

from arttrip.application.domain.auth.social_provider import SocialProvider
from arttrip.application.domain.user.role import UserRole
from arttrip.application.domain.user.user import User


class UserPort(ABC):
    @abstractmethod
    def add(self, user: User) -> None:
        pass

    @abstractmethod
    def find_by_social_identity(
        self, *, provider: SocialProvider, provider_user_id: str
    ) -> User | None:
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    def is_nickname_taken(self, *, nickname: str, except_user_id: int) -> bool:
        pass

    @abstractmethod
    def find_ids_by_role(self, role: UserRole) -> list[int]:
        pass

    @abstractmethod
    def remove_with_owned_data(self, user_id: int) -> None:
        pass

    @abstractmethod
    def find_by_id_for_update(self, user_id: int) -> User | None:
        pass
