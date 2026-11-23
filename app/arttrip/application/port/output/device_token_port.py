from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Collection


@dataclass(frozen=True)
class PushTarget:
    user_id: int
    token: str


class DeviceTokenPort(ABC):
    @abstractmethod
    def assign_to_user(self, *, user_id: int, token: str) -> None:
        pass

    @abstractmethod
    def clear_for_user(self, user_id: int) -> None:
        pass

    @abstractmethod
    def find_push_targets(self, user_ids: Collection[int]) -> list[PushTarget]:
        pass

    @abstractmethod
    def clear_tokens(self, tokens: Collection[str]) -> None:
        pass

    @abstractmethod
    def find_all_push_targets(self) -> list[PushTarget]:
        pass
