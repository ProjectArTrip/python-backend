from typing import Annotated

from fastapi import Depends

from arttrip.application.port.input.favorite.use_cases import (
    AddFavoriteUseCase,
    ListFavoritesUseCase,
    RemoveFavoriteUseCase,
)


def provide_add_favorite_use_case() -> AddFavoriteUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_remove_favorite_use_case() -> RemoveFavoriteUseCase:
    raise NotImplementedError("composition root must override this dependency")


AddFavoriteUseCaseDep = Annotated[
    AddFavoriteUseCase, Depends(provide_add_favorite_use_case)
]


RemoveFavoriteUseCaseDep = Annotated[
    RemoveFavoriteUseCase, Depends(provide_remove_favorite_use_case)
]


def provide_list_favorites_use_case() -> ListFavoritesUseCase:
    raise NotImplementedError("composition root must override this dependency")


ListFavoritesUseCaseDep = Annotated[
    ListFavoritesUseCase, Depends(provide_list_favorites_use_case)
]
