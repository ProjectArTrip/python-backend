from datetime import UTC, datetime

import pytest
from arttrip.application.domain.notification.notification import (
    BODY_MAX_LENGTH,
    RETENTION_DAYS,
    Notification,
    get_retention_start,
)
from arttrip.application.util.exception import DomainException

NOW = datetime(2026, 11, 11, 12, 0, tzinfo=UTC)
LATER = datetime(2026, 11, 12, 12, 0, tzinfo=UTC)
OWNER_ID = 1
OTHER_USER_ID = 2


class TestNotification:
    # 막는 것: 아주 긴 닉네임(과대 입력)으로 알림 본문이 칼럼 길이를 넘어
    # 인증 요청 저장까지 함께 실패하는 것.
    def test_긴_닉네임이_들어와도_본문은_칼럼_길이를_넘지_않는다(self) -> None:
        # given
        long_nickname = "가" * 1000

        # when
        notification = Notification.artist_application_submitted(
            admin_id=99, applicant_nickname=long_nickname, application_id=1, now=NOW
        )

        # then
        assert len(notification.body) == BODY_MAX_LENGTH

    # 막는 것: 읽음 요청의 중복 전송으로 처음 읽은 시각이 덮어써지는 것.
    def test_읽음_처리를_반복해도_처음_읽은_시각을_유지한다(self) -> None:
        # given
        notification = Notification.artist_application_approved(
            applicant_id=OWNER_ID, application_id=1, now=NOW
        )
        notification.mark_read(now=NOW)

        # when
        notification.mark_read(now=LATER)

        # then
        assert notification.is_read is True
        assert notification.read_at == NOW

    # 막는 것: 알림 ID 를 바꿔 넣어 남의 알림을 읽음 처리하는 것 (OWASP A01:2025 Broken Access Control).
    def test_남의_알림은_읽음_처리할_수_없다(self) -> None:
        # given
        notification = Notification.artist_application_approved(
            applicant_id=OWNER_ID, application_id=1, now=NOW
        )

        # when
        with pytest.raises(DomainException) as raised:
            notification.mark_read_by(user_id=OTHER_USER_ID, now=NOW)

        # then
        # 403 이 아니라 "없음"으로 답해 그 알림이 존재한다는 사실을 알리지 않는다.
        assert raised.value.code == "NOTIFICATION_NOT_FOUND"
        assert notification.is_read is False
        assert notification.read_at is None

    # 막는 것: 보관 기간 경계에서 하루가 더 보이거나 덜 보이는 것 (경계값).
    def test_보관_시작_시각은_정확히_보관_기간만큼_전이다(self) -> None:
        # given
        # when
        start = get_retention_start(NOW)

        # then
        assert (NOW - start).days == RETENTION_DAYS
        assert (NOW - start).seconds == 0
