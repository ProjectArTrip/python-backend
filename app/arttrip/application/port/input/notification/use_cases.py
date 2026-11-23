from abc import ABC, abstractmethod

from arttrip.application.port.input.notification.commands import (
    MarkNotificationReadCommand,
    SendPushCommand,
)
from arttrip.application.port.input.notification.queries import ListNotificationsQuery
from arttrip.application.port.input.notification.results import (
    NotificationView,
    PushDispatchResult,
)
from arttrip.application.port.input.pagination import CursorPage


class ListNotificationsUseCase(ABC):
    @abstractmethod
    def list_notifications(
        self, query: ListNotificationsQuery
    ) -> CursorPage[NotificationView]:
        pass


class CountUnreadNotificationsUseCase(ABC):
    @abstractmethod
    def count_unread_notifications(self, user_id: int) -> int:
        pass


class MarkNotificationReadUseCase(ABC):
    @abstractmethod
    def mark_notification_read(self, command: MarkNotificationReadCommand) -> None:
        pass


class MarkAllNotificationsReadUseCase(ABC):
    @abstractmethod
    def mark_all_notifications_read(self, user_id: int) -> None:
        pass


class SendPushUseCase(ABC):
    @abstractmethod
    def send_push(self, command: SendPushCommand) -> PushDispatchResult:
        pass
