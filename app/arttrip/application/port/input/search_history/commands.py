from dataclasses import dataclass


@dataclass(frozen=True)
class AddSearchHistoryCommand:
    user_id: int
    keyword: str


@dataclass(frozen=True)
class RemoveSearchHistoryCommand:
    user_id: int
    search_history_id: int
