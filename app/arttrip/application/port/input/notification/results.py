from dataclasses import dataclass
from datetime import datetime

from arttrip.application.domain.notification.notification_action import (
    NotificationAction,
)


@dataclass(frozen=True)
class NotificationView:
    notification_id: int
    action: NotificationAction
    reference_id: int | None
    title: str
    body: str
    is_read: bool
    created_at: datetime


@dataclass(frozen=True)
class PushDispatchResult:
    dispatch_id: int | None
    requested_users: int
    targeted_tokens: int
    succeeded: int
    failed: int
    removed_tokens: int
