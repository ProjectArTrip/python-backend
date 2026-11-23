from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from arttrip.application.domain.exhibit.exceptions import ExhibitError
from arttrip.application.domain.exhibit.exhibit_filter import ExhibitFilter
from arttrip.application.port.input.favorite.commands import (
    AddFavoriteCommand,
    RemoveFavoriteCommand,
)
from arttrip.application.port.input.favorite.queries import ListFavoritesQuery
from arttrip.inbound.http.dependencies.auth import CurrentUserDep
from arttrip.inbound.http.dependencies.favorite import (
    AddFavoriteUseCaseDep,
    ListFavoritesUseCaseDep,
    RemoveFavoriteUseCaseDep,
)
from arttrip.inbound.http.openapi import AUTHENTICATION_ERRORS, error_responses
from arttrip.inbound.http.routes.exhibits import to_exhibit_summary_response
from arttrip.inbound.http.schemas.favorites import (
    FavoriteListParams,
    FavoriteListResponse,
)

router = APIRouter()


@router.post(
    "/{exhibit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=error_responses(*AUTHENTICATION_ERRORS, ExhibitError.not_found),
)
def add_favorite(
    exhibit_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUserDep,
    use_case: AddFavoriteUseCaseDep,
) -> None:
    use_case.add_favorite(
        AddFavoriteCommand(user_id=current_user.user_id, exhibit_id=exhibit_id)
    )


@router.delete(
    "/{exhibit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=error_responses(*AUTHENTICATION_ERRORS),
)
def remove_favorite(
    exhibit_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUserDep,
    use_case: RemoveFavoriteUseCaseDep,
) -> None:
    use_case.remove_favorite(
        RemoveFavoriteCommand(user_id=current_user.user_id, exhibit_id=exhibit_id)
    )


@router.get(
    "",
    response_model=FavoriteListResponse,
    responses=error_responses(*AUTHENTICATION_ERRORS),
)
def list_favorites(
    current_user: CurrentUserDep,
    use_case: ListFavoritesUseCaseDep,
    params: Annotated[FavoriteListParams, Query()],
) -> FavoriteListResponse:
    criteria = ExhibitFilter(
        domestic=params.domestic,
        country_code=(
            params.country_code.upper() if params.country_code is not None else None
        ),
        regions=frozenset({params.region})
        if params.region is not None
        else frozenset(),
    )
    result = use_case.list_favorites(
        ListFavoritesQuery(
            user_id=current_user.user_id,
            criteria=criteria,
            sort=params.sort_type,
            cursor=params.cursor,
            size=params.size,
        )
    )
    return FavoriteListResponse(
        favorites=[to_exhibit_summary_response(item) for item in result.page.items],
        total_count=result.total_count,
        next_cursor=result.page.next_cursor,
        has_next=result.page.has_next,
    )
