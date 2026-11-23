from enum import StrEnum


class PushDeliveryStatus(StrEnum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    STALE = "STALE"
