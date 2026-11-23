from collections.abc import Mapping, Sequence

from arttrip.application.domain.notification.push_delivery import PushDelivery
from arttrip.application.domain.notification.push_delivery_status import (
    PushDeliveryStatus,
)


class PushDispatch:
    def __init__(
        self, *, id_: int | None, title: str, body: str, data: Mapping[str, str]
    ) -> None:
        self._id = id_
        self.title = title
        self.body = body
        self.data = dict(data)
        self.deliveries: list[PushDelivery] = []

    @property
    def id(self) -> int | None:
        return self._id

    @classmethod
    def create(
        cls,
        *,
        title: str,
        body: str,
        data: Mapping[str, str],
        deliveries: Sequence[PushDelivery],
    ) -> "PushDispatch":
        dispatch = cls(id_=None, title=title, body=body, data=data)
        dispatch.deliveries.extend(deliveries)
        return dispatch

    @property
    def success_count(self) -> int:
        return sum(1 for d in self.deliveries if d.status is PushDeliveryStatus.SENT)

    @property
    def failure_count(self) -> int:
        return sum(
            1
            for d in self.deliveries
            if d.status in (PushDeliveryStatus.FAILED, PushDeliveryStatus.STALE)
        )
