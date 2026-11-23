from typing import Annotated

from fastapi import APIRouter, Path, status

from arttrip.application.domain.notification.exceptions import NotificationError
from arttrip.application.port.input.notification.commands import (
    MarkNotificationReadCommand,
)
from arttrip.application.port.input.notification.queries import ListNotificationsQuery
from arttrip.inbound.http.dependencies.auth import CurrentUserDep
from arttrip.inbound.http.dependencies.notification import (
    CountUnreadNotificationsUseCaseDep,
    ListNotificationsUseCaseDep,
    MarkAllNotificationsReadUseCaseDep,
    MarkNotificationReadUseCaseDep,
)
from arttrip.inbound.http.openapi import AUTHENTICATION_ERRORS, error_responses
from arttrip.inbound.http.pagination import (
    DEFAULT_PAGE_SIZE,
    CursorParam,
    PageSizeParam,
)
from arttrip.inbound.http.schemas.notifications import (
    NotificationListResponse,
    NotificationResponse,
    UnreadCountResponse,
)

router = APIRouter()


@router.get(
    "",
    response_model=NotificationListResponse,
    responses=error_responses(*AUTHENTICATION_ERRORS),
)
def list_notifications(
    current_user: CurrentUserDep,
    use_case: ListNotificationsUseCaseDep,
    cursor: CursorParam = None,
    size: PageSizeParam = DEFAULT_PAGE_SIZE,
) -> NotificationListResponse:
    page = use_case.list_notifications(
        ListNotificationsQuery(user_id=current_user.user_id, cursor=cursor, size=size)
    )
    return NotificationListResponse(
        notifications=[
            NotificationResponse(
                id=item.notification_id,
                action=item.action,
                reference_id=item.reference_id,
                title=item.title,
                body=item.body,
                is_read=item.is_read,
                created_at=item.created_at,
            )
            for item in page.items
        ],
        next_cursor=page.next_cursor,
        has_next=page.has_next,
    )


@router.get(
    "/unreadCount",
    response_model=UnreadCountResponse,
    responses=error_responses(*AUTHENTICATION_ERRORS),
)
def count_unread_notifications(
    current_user: CurrentUserDep,
    use_case: CountUnreadNotificationsUseCaseDep,
) -> UnreadCountResponse:
    unread_count = use_case.count_unread_notifications(current_user.user_id)
    return UnreadCountResponse(unread_count=unread_count)


@router.post(
    "/readAll",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=error_responses(*AUTHENTICATION_ERRORS),
)
def mark_all_notifications_read(
    current_user: CurrentUserDep,
    use_case: MarkAllNotificationsReadUseCaseDep,
) -> None:
    use_case.mark_all_notifications_read(current_user.user_id)


@router.post(
    "/{notification_id}/read",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=error_responses(*AUTHENTICATION_ERRORS, NotificationError.not_found),
)
def mark_notification_read(
    notification_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUserDep,
    use_case: MarkNotificationReadUseCaseDep,
) -> None:
    use_case.mark_notification_read(
        MarkNotificationReadCommand(
            user_id=current_user.user_id, notification_id=notification_id
        )
    )
