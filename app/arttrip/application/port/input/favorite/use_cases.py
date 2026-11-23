from abc import ABC, abstractmethod

from arttrip.application.port.input.favorite.commands import (
    AddFavoriteCommand,
    RemoveFavoriteCommand,
)
from arttrip.application.port.input.favorite.queries import ListFavoritesQuery
from arttrip.application.port.input.favorite.results import ListFavoritesResult


class AddFavoriteUseCase(ABC):
    @abstractmethod
    def add_favorite(self, command: AddFavoriteCommand) -> None:
        pass


class RemoveFavoriteUseCase(ABC):
    @abstractmethod
    def remove_favorite(self, command: RemoveFavoriteCommand) -> None:
        pass


class ListFavoritesUseCase(ABC):
    @abstractmethod
    def list_favorites(self, query: ListFavoritesQuery) -> ListFavoritesResult:
        pass
