from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from arttrip.application.domain.notification.push_delivery_status import (
    PushDeliveryStatus,
)


@dataclass(frozen=True)
class PushMessage:
    title: str
    body: str
    data: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class PushOutcome:
    token: str
    status: PushDeliveryStatus
    message_id: str | None
    error_code: str | None


@dataclass(frozen=True)
class PushSendResult:
    outcomes: tuple[PushOutcome, ...]

    @property
    def stale_tokens(self) -> frozenset[str]:
        return frozenset(
            o.token for o in self.outcomes if o.status is PushDeliveryStatus.STALE
        )


class PushSenderPort(ABC):
    @abstractmethod
    def send(self, *, tokens: Sequence[str], message: PushMessage) -> PushSendResult:
        pass
