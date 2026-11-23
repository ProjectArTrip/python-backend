from abc import ABC, abstractmethod

from arttrip.application.domain.search_history.search_history import SearchHistory


class SearchHistoryPort(ABC):
    @abstractmethod
    def add(self, history: SearchHistory) -> None:
        pass

    @abstractmethod
    def keep_latest(self, *, user_id: int, count: int) -> None:
        pass

    @abstractmethod
    def list_recent(self, *, user_id: int, limit: int) -> list[SearchHistory]:
        pass

    @abstractmethod
    def remove(self, *, user_id: int, history_id: int) -> int | None:
        pass

    @abstractmethod
    def remove_all(self, user_id: int) -> None:
        pass
