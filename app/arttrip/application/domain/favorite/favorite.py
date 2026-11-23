from datetime import datetime

from arttrip.application.util.utc import to_utc


class Favorite:
    def __init__(
        self,
        *,
        id_: int | None,
        user_id: int,
        exhibit_id: int,
        created_at: datetime,
    ) -> None:
        self._id = id_
        self.user_id = user_id
        self.exhibit_id = exhibit_id
        self.created_at = to_utc(created_at)

    @property
    def id(self) -> int | None:
        return self._id

    @classmethod
    def create(cls, *, user_id: int, exhibit_id: int, now: datetime) -> "Favorite":
        return cls(id_=None, user_id=user_id, exhibit_id=exhibit_id, created_at=now)
