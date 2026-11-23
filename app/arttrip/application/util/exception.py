from enum import StrEnum


class ErrorCode(StrEnum):
    INVALID_ARGUMENT = "INVALID_ARGUMENT"
    UNAUTHENTICATED = "UNAUTHENTICATED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_FOUND = "NOT_FOUND"


class DomainException(Exception):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        error_code: ErrorCode = ErrorCode.INVALID_ARGUMENT,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.error_code = error_code
