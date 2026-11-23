from fastapi import Request

from arttrip.application.domain.notification.notification_services import (
    CountUnreadNotificationsService,
    ListNotificationsService,
    MarkAllNotificationsReadService,
    MarkNotificationReadService,
    SendPushService,
)
from arttrip.application.port.input.notification.use_cases import (
    CountUnreadNotificationsUseCase,
    ListNotificationsUseCase,
    MarkAllNotificationsReadUseCase,
    MarkNotificationReadUseCase,
    SendPushUseCase,
)
from arttrip.bootstrap.wiring.common import Overrides, new_unit_of_work
from arttrip.inbound.http.dependencies.notification import (
    provide_count_unread_notifications_use_case,
    provide_list_notifications_use_case,
    provide_mark_all_notifications_read_use_case,
    provide_mark_notification_read_use_case,
    provide_send_push_use_case,
)


def build_list_notifications_use_case(request: Request) -> ListNotificationsUseCase:
    return ListNotificationsService(uow=new_unit_of_work(request))


def build_count_unread_notifications_use_case(
    request: Request,
) -> CountUnreadNotificationsUseCase:
    return CountUnreadNotificationsService(uow=new_unit_of_work(request))


def build_mark_notification_read_use_case(
    request: Request,
) -> MarkNotificationReadUseCase:
    return MarkNotificationReadService(uow=new_unit_of_work(request))


def build_mark_all_notifications_read_use_case(
    request: Request,
) -> MarkAllNotificationsReadUseCase:
    return MarkAllNotificationsReadService(uow=new_unit_of_work(request))


def build_send_push_use_case(request: Request) -> SendPushUseCase:
    return SendPushService(
        uow=new_unit_of_work(request),
        push_sender=request.app.state.push_sender,
    )


def wire_notification(overrides: Overrides) -> None:
    overrides[provide_list_notifications_use_case] = build_list_notifications_use_case
    overrides[provide_count_unread_notifications_use_case] = (
        build_count_unread_notifications_use_case
    )
    overrides[provide_mark_notification_read_use_case] = (
        build_mark_notification_read_use_case
    )
    overrides[provide_mark_all_notifications_read_use_case] = (
        build_mark_all_notifications_read_use_case
    )
    overrides[provide_send_push_use_case] = build_send_push_use_case
