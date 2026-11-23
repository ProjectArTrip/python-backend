from datetime import UTC, datetime

from arttrip.application.util.exception import DomainException


class NaiveDatetimeException(DomainException):
    def __init__(self) -> None:
        super().__init__(
            code="DATETIME_NAIVE",
            message="datetime must be timezone-aware",
        )


def to_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise NaiveDatetimeException()
    return value.astimezone(UTC)
