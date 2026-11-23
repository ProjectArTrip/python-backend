from arttrip.application.util.exception import DomainException, ErrorCode


class NotificationError(DomainException):
    @classmethod
    def not_found(cls) -> "NotificationError":
        return cls(
            code="NOTIFICATION_NOT_FOUND",
            message="알림을 찾을 수 없습니다.",
            error_code=ErrorCode.NOT_FOUND,
        )
