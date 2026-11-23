from abc import ABC, abstractmethod
from datetime import datetime


class AccessTokenDenylistPort(ABC):
    @abstractmethod
    def deny(self, *, token_id: str, expires_at: datetime) -> None:
        pass

    @abstractmethod
    def is_denied(self, token_id: str) -> bool:
        pass
