import logging
from datetime import UTC, datetime

from arttrip.application.domain.notification.exceptions import NotificationError
from arttrip.application.domain.notification.notification import (
    Notification,
    get_retention_start,
)
from arttrip.application.domain.notification.push_delivery import PushDelivery
from arttrip.application.domain.notification.push_dispatch import PushDispatch
from arttrip.application.port.input.notification.commands import (
    MarkNotificationReadCommand,
    SendPushCommand,
)
from arttrip.application.port.input.notification.queries import ListNotificationsQuery
from arttrip.application.port.input.notification.results import (
    NotificationView,
    PushDispatchResult,
)
from arttrip.application.port.input.notification.use_cases import (
    CountUnreadNotificationsUseCase,
    ListNotificationsUseCase,
    MarkAllNotificationsReadUseCase,
    MarkNotificationReadUseCase,
    SendPushUseCase,
)
from arttrip.application.port.input.pagination import CursorPage
from arttrip.application.port.output.push_sender_port import PushMessage, PushSenderPort
from arttrip.application.port.output.unit_of_work import UnitOfWork

_logger = logging.getLogger(__name__)


class ListNotificationsService(ListNotificationsUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def list_notifications(
        self, query: ListNotificationsQuery
    ) -> CursorPage[NotificationView]:
        since = get_retention_start(datetime.now(UTC))
        with self._uow as uow:
            rows = uow.notifications.list_page(
                user_id=query.user_id,
                since=since,
                cursor=query.cursor,
                limit=query.size + 1,
            )
            has_next = len(rows) > query.size
            items = tuple(_to_view(row) for row in rows[: query.size])
            next_cursor = items[-1].notification_id if has_next else None
            return CursorPage(items=items, next_cursor=next_cursor)


class CountUnreadNotificationsService(CountUnreadNotificationsUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def count_unread_notifications(self, user_id: int) -> int:
        since = get_retention_start(datetime.now(UTC))
        with self._uow as uow:
            return uow.notifications.count_unread(user_id=user_id, since=since)


class MarkNotificationReadService(MarkNotificationReadUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def mark_notification_read(self, command: MarkNotificationReadCommand) -> None:
        with self._uow as uow:
            notification = uow.notifications.find_by_id(command.notification_id)
            if notification is None:
                raise NotificationError.not_found()
            notification.mark_read_by(user_id=command.user_id, now=datetime.now(UTC))


class MarkAllNotificationsReadService(MarkAllNotificationsReadUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def mark_all_notifications_read(self, user_id: int) -> None:
        with self._uow as uow:
            uow.notifications.mark_all_read(user_id=user_id, now=datetime.now(UTC))


def _to_view(notification: Notification) -> NotificationView:
    notification_id = notification.id
    if notification_id is None:
        raise RuntimeError("notification loaded from storage must have an id")
    return NotificationView(
        notification_id=notification_id,
        action=notification.action,
        reference_id=notification.reference_id,
        title=notification.title,
        body=notification.body,
        is_read=notification.is_read,
        created_at=notification.created_at,
    )


class SendPushService(SendPushUseCase):
    def __init__(self, *, uow: UnitOfWork, push_sender: PushSenderPort) -> None:
        self._uow = uow
        self._push_sender = push_sender

    def send_push(self, command: SendPushCommand) -> PushDispatchResult:
        requested_users = len(command.user_ids)

        with self._uow as uow:
            targets = (
                uow.device_tokens.find_push_targets(command.user_ids) * command.repeat
            )

            if not targets:
                _logger.info("push skipped: requested=%d targets=0", requested_users)
                return PushDispatchResult(
                    dispatch_id=None,
                    requested_users=requested_users,
                    targeted_tokens=0,
                    succeeded=0,
                    failed=0,
                    removed_tokens=0,
                )
            dispatch = PushDispatch.create(
                title=command.title,
                body=command.body,
                data=command.data,
                deliveries=[
                    PushDelivery.pending(user_id=target.user_id, token=target.token)
                    for target in targets
                ],
            )

            uow.push_dispatches.add(dispatch)
            dispatch_id = dispatch.id

        if dispatch_id is None:
            raise RuntimeError("push dispatch must be persisted before sending")

        sent = self._push_sender.send(
            tokens=[target.token for target in targets],
            message=PushMessage(
                title=command.title, body=command.body, data=command.data
            ),
        )

        with self._uow as uow:
            stored = uow.push_dispatches.find_by_id(dispatch_id)
            if stored is None:
                raise RuntimeError("push dispatch disappeared before recording")
            for delivery, outcome in zip(stored.deliveries, sent.outcomes, strict=True):
                delivery.record(
                    status=outcome.status,
                    message_id=outcome.message_id,
                    error_code=outcome.error_code,
                )
            if sent.stale_tokens:
                uow.device_tokens.clear_tokens(sent.stale_tokens)
            succeeded = stored.success_count
            failed = stored.failure_count

        _logger.info(
            "push dispatched: id=%d requested=%d targets=%d success=%d failure=%d removed=%d",
            dispatch_id,
            requested_users,
            len(targets),
            succeeded,
            failed,
            len(sent.stale_tokens),
        )
        return PushDispatchResult(
            dispatch_id=dispatch_id,
            requested_users=requested_users,
            targeted_tokens=len(targets),
            succeeded=succeeded,
            failed=failed,
            removed_tokens=len(sent.stale_tokens),
        )
