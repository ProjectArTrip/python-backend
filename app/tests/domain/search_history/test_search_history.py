from datetime import UTC, datetime

import pytest
from arttrip.application.domain.search_history.search_history import SearchHistory
from arttrip.application.domain.search_history.search_history_policy import (
    SearchHistoryPolicy,
)
from arttrip.application.util.exception import DomainException

NOW = datetime(2026, 11, 16, 12, 0, tzinfo=UTC)
POLICY = SearchHistoryPolicy(max_count=10, max_length=50)


class TestSearchHistory:
    @pytest.mark.parametrize("keyword", ["", "   ", "\t\u3000"])
    def test_공백_검색_실패(self, keyword: str) -> None:
        # when
        with pytest.raises(DomainException) as raised:
            SearchHistory.create(user_id=1, keyword=keyword, policy=POLICY, now=NOW)

        # then
        assert raised.value.code == "SEARCH_HISTORY_KEYWORD_BLANK"

    def test_길이_상한을_넘으면_거부한다(self) -> None:
        # when
        with pytest.raises(DomainException) as raised:
            SearchHistory.create(user_id=1, keyword="가" * 51, policy=POLICY, now=NOW)

        # then
        assert raised.value.code == "SEARCH_HISTORY_KEYWORD_TOO_LONG"
