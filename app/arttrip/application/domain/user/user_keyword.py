from datetime import datetime

from arttrip.application.util.utc import to_utc


class UserKeyword:
    def __init__(
        self, *, id_: int | None, keyword_id: int, selected_at: datetime
    ) -> None:
        self._id = id_
        self.keyword_id = keyword_id
        self.selected_at = to_utc(selected_at)

    @property
    def id(self) -> int | None:
        return self._id
