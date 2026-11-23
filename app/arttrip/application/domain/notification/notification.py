from datetime import datetime, timedelta
from typing import Final

from arttrip.application.domain.notification.exceptions import NotificationError
from arttrip.application.domain.notification.notification_action import (
    NotificationAction,
)
from arttrip.application.util.utc import to_utc

TITLE_MAX_LENGTH: Final = 255
BODY_MAX_LENGTH: Final = 255
RETENTION_DAYS: Final = 30

_ARTIST_REQUEST_TITLE: Final = "아티스트 인증"
_SUBMITTED_BODY: Final = "{nickname} 님이 아티스트 인증을 요청했습니다."
_APPROVED_BODY: Final = "아티스트 인증이 승인되었습니다."
_REJECTED_BODY: Final = "아티스트 인증 요청이 반려되었습니다. 사유를 확인해 주세요."
_NEW_EXHIBIT_TITLE: Final = "새로운 전시가 업데이트되었습니다"
_NEW_EXHIBIT_BODY: Final = "오늘 새롭게 공개된 전시가 있어요. {hall_name}의 ‘{exhibit_title}’ 전시를 지금 확인해보세요."
_NEW_EXHIBIT_PERSONALIZED_BODY: Final = (
    "회원님의 관심 장르와 스타일에 맞는 전시가 새로 공개되었어요. "
    "{hall_name}의 ‘{exhibit_title}’ 전시를 지금 확인해보세요."
)


def get_retention_start(now: datetime) -> datetime:
    return now - timedelta(days=RETENTION_DAYS)


class Notification:
    def __init__(
        self,
        *,
        id_: int | None,
        user_id: int,
        title: str,
        body: str,
        action: NotificationAction,
        reference_id: int | None,
        is_read: bool,
        read_at: datetime | None,
        created_at: datetime,
    ) -> None:
        self._id = id_
        self.user_id = user_id
        self.title = title[:TITLE_MAX_LENGTH]
        self.body = body[:BODY_MAX_LENGTH]
        self.action = action
        self.reference_id = reference_id
        self.is_read = is_read
        self.read_at = read_at
        self.created_at = to_utc(created_at)

    @property
    def id(self) -> int | None:
        return self._id

    @classmethod
    def _unread(
        cls,
        *,
        user_id: int,
        title: str,
        body: str,
        action: NotificationAction,
        reference_id: int,
        now: datetime,
    ) -> "Notification":
        return cls(
            id_=None,
            user_id=user_id,
            title=title,
            body=body,
            action=action,
            reference_id=reference_id,
            is_read=False,
            read_at=None,
            created_at=now,
        )

    @classmethod
    def artist_application_submitted(
        cls,
        *,
        admin_id: int,
        applicant_nickname: str,
        application_id: int,
        now: datetime,
    ) -> "Notification":
        return cls._unread(
            user_id=admin_id,
            body=_SUBMITTED_BODY.format(nickname=applicant_nickname),
            action=NotificationAction.MOVE_ARTIST_REQUEST_REVIEW,
            reference_id=application_id,
            now=now,
            title=_ARTIST_REQUEST_TITLE,
        )

    @classmethod
    def artist_application_approved(
        cls, *, applicant_id: int, application_id: int, now: datetime
    ) -> "Notification":
        return cls._unread(
            user_id=applicant_id,
            body=_APPROVED_BODY,
            action=NotificationAction.MOVE_ARTIST_REQUEST,
            reference_id=application_id,
            now=now,
            title=_ARTIST_REQUEST_TITLE,
        )

    @classmethod
    def artist_application_rejected(
        cls, *, applicant_id: int, application_id: int, now: datetime
    ) -> "Notification":
        return cls._unread(
            user_id=applicant_id,
            body=_REJECTED_BODY,
            action=NotificationAction.MOVE_ARTIST_REQUEST,
            reference_id=application_id,
            now=now,
            title=_ARTIST_REQUEST_TITLE,
        )

    @classmethod
    def exhibit_registered(
        cls,
        *,
        user_id: int,
        exhibit_id: int,
        hall_name: str,
        exhibit_title: str,
        personalized: bool,
        now: datetime,
    ) -> "Notification":
        template = _NEW_EXHIBIT_PERSONALIZED_BODY if personalized else _NEW_EXHIBIT_BODY
        return cls._unread(
            user_id=user_id,
            title=_NEW_EXHIBIT_TITLE,
            body=template.format(hall_name=hall_name, exhibit_title=exhibit_title),
            action=NotificationAction.MOVE_EXHIBIT_DETAIL,
            reference_id=exhibit_id,
            now=now,
        )

    def mark_read_by(self, *, user_id: int, now: datetime) -> None:
        if self.user_id != user_id:
            raise NotificationError.not_found()
        self.mark_read(now=now)

    def mark_read(self, *, now: datetime) -> None:
        if self.is_read:
            return
        self.is_read = True
        self.read_at = to_utc(now)
