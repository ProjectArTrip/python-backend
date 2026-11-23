from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True)
class MarkNotificationReadCommand:
    user_id: int
    notification_id: int


@dataclass(frozen=True)
class SendPushCommand:
    user_ids: tuple[int, ...]
    title: str
    body: str
    data: Mapping[str, str] = field(default_factory=dict)
    repeat: int = 1
