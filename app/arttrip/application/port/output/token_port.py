from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from arttrip.application.domain.user.role import UserRole


@dataclass(frozen=True)
class AccessTokenClaims:
    user_id: int
    role: UserRole
    token_id: str
    expires_at: datetime


class TokenPort(ABC):
    @abstractmethod
    def issue_access_token(self, *, user_id: int, role: UserRole, now: datetime) -> str:
        pass

    @abstractmethod
    def verify_access_token(self, token: str) -> AccessTokenClaims:
        pass
