from dataclasses import dataclass


@dataclass(frozen=True)
class ListNotificationsQuery:
    user_id: int
    cursor: int | None
    size: int
