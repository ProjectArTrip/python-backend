from abc import ABC, abstractmethod

from arttrip.application.port.input.search_history.commands import (
    AddSearchHistoryCommand,
    RemoveSearchHistoryCommand,
)
from arttrip.application.port.input.search_history.results import SearchHistoryItem


class AddSearchHistoryUseCase(ABC):
    @abstractmethod
    def add_search_history(self, command: AddSearchHistoryCommand) -> None:
        pass


class ListSearchHistoryUseCase(ABC):
    @abstractmethod
    def list_search_history(self, user_id: int) -> tuple[SearchHistoryItem, ...]:
        pass


class RemoveSearchHistoryUseCase(ABC):
    @abstractmethod
    def remove_search_history(self, command: RemoveSearchHistoryCommand) -> None:
        pass


class ClearSearchHistoryUseCase(ABC):
    @abstractmethod
    def clear_search_history(self, user_id: int) -> None:
        pass
