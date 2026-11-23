from datetime import datetime

from arttrip.application.domain.search_history.exceptions import SearchHistoryError
from arttrip.application.domain.search_history.search_history_policy import (
    SearchHistoryPolicy,
)
from arttrip.application.util.utc import to_utc


class SearchHistory:
    def __init__(
        self, *, id_: int | None, user_id: int, content: str, created_at: datetime
    ) -> None:
        self._id = id_
        self.user_id = user_id
        self.content = content
        self.created_at = to_utc(created_at)

    @property
    def id(self) -> int | None:
        return self._id

    @classmethod
    def create(
        cls, *, user_id: int, keyword: str, policy: SearchHistoryPolicy, now: datetime
    ) -> "SearchHistory":
        content = keyword.strip()
        if not content:
            raise SearchHistoryError.blank_keyword()
        if len(content) > policy.max_length:
            raise SearchHistoryError.keyword_too_long()
        return cls(id_=None, user_id=user_id, content=content, created_at=now)
