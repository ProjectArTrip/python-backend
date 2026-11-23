from dataclasses import dataclass


@dataclass(frozen=True)
class AddFavoriteCommand:
    user_id: int
    exhibit_id: int


@dataclass(frozen=True)
class RemoveFavoriteCommand:
    user_id: int
    exhibit_id: int
