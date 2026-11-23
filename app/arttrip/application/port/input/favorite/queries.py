from dataclasses import dataclass

from arttrip.application.domain.exhibit.exhibit_filter import ExhibitFilter
from arttrip.application.domain.favorite.favorite_sort import FavoriteSort


@dataclass(frozen=True)
class ListFavoritesQuery:
    user_id: int
    criteria: ExhibitFilter
    sort: FavoriteSort
    cursor: int | None
    size: int
