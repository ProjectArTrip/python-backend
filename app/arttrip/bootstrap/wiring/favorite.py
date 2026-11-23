from fastapi import Request

from arttrip.application.domain.favorite.favorite_services import (
    AddFavoriteService,
    ListFavoritesService,
    RemoveFavoriteService,
)
from arttrip.application.port.input.favorite.use_cases import (
    AddFavoriteUseCase,
    ListFavoritesUseCase,
    RemoveFavoriteUseCase,
)
from arttrip.bootstrap.wiring.common import Overrides, new_unit_of_work
from arttrip.inbound.http.dependencies.favorite import (
    provide_add_favorite_use_case,
    provide_list_favorites_use_case,
    provide_remove_favorite_use_case,
)


def build_add_favorite_use_case(request: Request) -> AddFavoriteUseCase:
    return AddFavoriteService(uow=new_unit_of_work(request))


def build_remove_favorite_use_case(request: Request) -> RemoveFavoriteUseCase:
    return RemoveFavoriteService(uow=new_unit_of_work(request))


def build_list_favorites_use_case(request: Request) -> ListFavoritesUseCase:
    return ListFavoritesService(
        uow=new_unit_of_work(request),
        status_policy=request.app.state.exhibit_status_policy,
    )


def wire_favorite(overrides: Overrides) -> None:
    overrides[provide_list_favorites_use_case] = build_list_favorites_use_case
    overrides[provide_add_favorite_use_case] = build_add_favorite_use_case
    overrides[provide_remove_favorite_use_case] = build_remove_favorite_use_case
