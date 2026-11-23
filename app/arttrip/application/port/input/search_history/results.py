from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SearchHistoryItem:
    search_history_id: int
    keyword: str
    searched_at: datetime
