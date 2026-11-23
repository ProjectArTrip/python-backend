from abc import ABC, abstractmethod


class RefreshTokenPort(ABC):
    @abstractmethod
    def issue(self, *, user_id: int) -> str:
        pass

    @abstractmethod
    def consume(self, token: str) -> int | None:
        pass
