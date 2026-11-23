from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from arttrip.application.domain.notification.notification import Notification
from arttrip.application.port.output.notification_port import NotificationPort
from arttrip.outbound.persistence.models import user_notice_table


class NotificationAdapter(NotificationPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add_all(self, notifications: Sequence[Notification]) -> None:
        self._session.add_all(notifications)

    def find_by_id(self, notification_id: int) -> Notification | None:
        return self._session.get(Notification, notification_id)

    def list_page(
        self, *, user_id: int, since: datetime, cursor: int | None, limit: int
    ) -> list[Notification]:
        statement = (
            select(Notification)
            .where(
                user_notice_table.c.user_id == user_id,
                user_notice_table.c.created_at >= since,
            )
            .order_by(user_notice_table.c.id.desc())
            .limit(limit)
        )
        if cursor is not None:
            statement = statement.where(user_notice_table.c.id < cursor)
        return list(self._session.scalars(statement).all())

    def count_unread(self, *, user_id: int, since: datetime) -> int:
        statement = select(func.count(user_notice_table.c.id)).where(
            user_notice_table.c.user_id == user_id,
            user_notice_table.c.created_at >= since,
            user_notice_table.c.is_read.is_(False),
        )
        return self._session.scalar(statement) or 0

    def mark_all_read(self, *, user_id: int, now: datetime) -> None:
        statement = (
            update(user_notice_table)
            .where(
                user_notice_table.c.user_id == user_id,
                user_notice_table.c.is_read.is_(False),
            )
            .values(is_read=True, read_at=now)
        )
        self._session.execute(statement)
