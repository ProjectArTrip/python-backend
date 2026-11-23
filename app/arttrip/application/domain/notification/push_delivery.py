import hashlib

from arttrip.application.domain.notification.push_delivery_status import (
    PushDeliveryStatus,
)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class PushDelivery:
    def __init__(
        self,
        *,
        id_: int | None,
        user_id: int,
        token_hash: str,
        status: PushDeliveryStatus,
        message_id: str | None,
        error_code: str | None,
    ) -> None:
        self._id = id_
        self.user_id = user_id
        self.token_hash = token_hash
        self.status = status
        self.message_id = message_id
        self.error_code = error_code

    @property
    def id(self) -> int | None:
        return self._id

    @classmethod
    def pending(cls, *, user_id: int, token: str) -> "PushDelivery":
        return cls(
            id_=None,
            user_id=user_id,
            token_hash=hash_token(token),
            status=PushDeliveryStatus.PENDING,
            message_id=None,
            error_code=None,
        )

    def record(
        self,
        *,
        status: PushDeliveryStatus,
        message_id: str | None,
        error_code: str | None,
    ) -> None:
        if self.status is not PushDeliveryStatus.PENDING:
            raise ValueError("push delivery is already recorded")
        self.status = status
        self.message_id = message_id
        self.error_code = error_code
