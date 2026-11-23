from typing import Annotated

from fastapi import Depends

from arttrip.application.port.input.notification.use_cases import (
    CountUnreadNotificationsUseCase,
    ListNotificationsUseCase,
    MarkAllNotificationsReadUseCase,
    MarkNotificationReadUseCase,
    SendPushUseCase,
)


def provide_list_notifications_use_case() -> ListNotificationsUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_count_unread_notifications_use_case() -> CountUnreadNotificationsUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_mark_notification_read_use_case() -> MarkNotificationReadUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_mark_all_notifications_read_use_case() -> MarkAllNotificationsReadUseCase:
    raise NotImplementedError("composition root must override this dependency")


ListNotificationsUseCaseDep = Annotated[
    ListNotificationsUseCase, Depends(provide_list_notifications_use_case)
]


CountUnreadNotificationsUseCaseDep = Annotated[
    CountUnreadNotificationsUseCase,
    Depends(provide_count_unread_notifications_use_case),
]


MarkNotificationReadUseCaseDep = Annotated[
    MarkNotificationReadUseCase, Depends(provide_mark_notification_read_use_case)
]


MarkAllNotificationsReadUseCaseDep = Annotated[
    MarkAllNotificationsReadUseCase,
    Depends(provide_mark_all_notifications_read_use_case),
]


def provide_send_push_use_case() -> SendPushUseCase:
    raise NotImplementedError("composition root must override this dependency")


SendPushUseCaseDep = Annotated[SendPushUseCase, Depends(provide_send_push_use_case)]
