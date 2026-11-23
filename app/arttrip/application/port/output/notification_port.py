from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import datetime

from arttrip.application.domain.notification.notification import Notification


class NotificationPort(ABC):
    @abstractmethod
    def add_all(self, notifications: Sequence[Notification]) -> None:
        pass

    @abstractmethod
    def find_by_id(self, notification_id: int) -> Notification | None:
        pass

    @abstractmethod
    def list_page(
        self, *, user_id: int, since: datetime, cursor: int | None, limit: int
    ) -> list[Notification]:
        pass

    @abstractmethod
    def count_unread(self, *, user_id: int, since: datetime) -> int:
        pass

    @abstractmethod
    def mark_all_read(self, *, user_id: int, now: datetime) -> None:
        pass
