from datetime import datetime

from arttrip.application.domain.notification.notification_action import (
    NotificationAction,
)
from arttrip.inbound.http.schemas.base import ApiModel


class NotificationResponse(ApiModel):
    id: int
    action: NotificationAction
    reference_id: int | None
    title: str
    body: str
    is_read: bool
    created_at: datetime


class NotificationListResponse(ApiModel):
    notifications: list[NotificationResponse]
    next_cursor: int | None
    has_next: bool


class UnreadCountResponse(ApiModel):
    unread_count: int
