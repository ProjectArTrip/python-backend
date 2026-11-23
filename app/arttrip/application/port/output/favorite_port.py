from abc import ABC, abstractmethod
from collections.abc import Collection
from dataclasses import dataclass
from datetime import date

from arttrip.application.domain.exhibit.exhibit import Exhibit
from arttrip.application.domain.exhibit.exhibit_filter import ExhibitFilter
from arttrip.application.domain.favorite.favorite import Favorite
from arttrip.application.domain.favorite.favorite_sort import FavoriteSort


@dataclass(frozen=True)
class FavoritedExhibit:
    exhibit: Exhibit
    cursor: int


class FavoritePort(ABC):
    @abstractmethod
    def add(self, favorite: Favorite) -> None:
        pass

    @abstractmethod
    def remove(self, *, user_id: int, exhibit_id: int) -> None:
        pass

    @abstractmethod
    def list_page(
        self,
        *,
        user_id: int,
        criteria: ExhibitFilter,
        sort: FavoriteSort,
        today: date,
        cursor: int | None,
        limit: int,
    ) -> list[FavoritedExhibit]:
        pass

    @abstractmethod
    def count(self, *, user_id: int, criteria: ExhibitFilter) -> int:
        pass

    @abstractmethod
    def find_exhibit_ids(
        self, *, user_id: int, exhibit_ids: Collection[int]
    ) -> set[int]:
        pass
