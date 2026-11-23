from fastapi import APIRouter, status

from arttrip.application.domain.exhibit.exceptions import ExhibitError
from arttrip.application.domain.user.exceptions import UserError
from arttrip.application.port.input.exhibit.commands import (
    DeleteArtistExhibitCommand,
    RegisterArtistExhibitCommand,
    UpdateArtistExhibitCommand,
)
from arttrip.application.port.input.exhibit.queries import ListArtistExhibitsQuery
from arttrip.inbound.http.dependencies.auth import CurrentUserDep
from arttrip.inbound.http.dependencies.exhibit import (
    DeleteArtistExhibitUseCaseDep,
    ListArtistExhibitsUseCaseDep,
    RegisterArtistExhibitUseCaseDep,
    UpdateArtistExhibitUseCaseDep,
)
from arttrip.inbound.http.openapi import AUTHENTICATION_ERRORS, error_responses
from arttrip.inbound.http.pagination import (
    DEFAULT_PAGE_SIZE,
    PageIndexParam,
    PageSizeParam,
)
from arttrip.inbound.http.routes.admin_exhibits import (
    ExhibitIdParam,
    to_list_item_response,
)
from arttrip.inbound.http.schemas.admin_exhibits import (
    AdminExhibitListItemResponse,
    CreateExhibitRequest,
    ExhibitCreatedResponse,
)
from arttrip.inbound.http.schemas.base import PageResponse

router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ExhibitCreatedResponse,
    responses=error_responses(
        *AUTHENTICATION_ERRORS,
        UserError.artist_role_required,
        ExhibitError.title_required,
        ExhibitError.invalid_schedule,
        ExhibitError.hall_name_required,
        ExhibitError.invalid_coordinates,
        ExhibitError.domestic_mismatch,
        ExhibitError.unknown_country,
        ExhibitError.unknown_keyword,
        ExhibitError.duplicate,
    ),
)
def register_artist_exhibit(
    body: CreateExhibitRequest,
    current_user: CurrentUserDep,
    use_case: RegisterArtistExhibitUseCaseDep,
) -> ExhibitCreatedResponse:
    exhibit_id = use_case.register_artist_exhibit(
        RegisterArtistExhibitCommand(
            artist_id=current_user.user_id,
            exhibit=body.to_command(),
        )
    )
    return ExhibitCreatedResponse(exhibit_id=exhibit_id)


@router.get(
    "",
    response_model=PageResponse[AdminExhibitListItemResponse],
    responses=error_responses(*AUTHENTICATION_ERRORS, UserError.artist_role_required),
)
def list_artist_exhibits(
    current_user: CurrentUserDep,
    use_case: ListArtistExhibitsUseCaseDep,
    page: PageIndexParam = 0,
    size: PageSizeParam = DEFAULT_PAGE_SIZE,
) -> PageResponse[AdminExhibitListItemResponse]:
    result = use_case.list_artist_exhibits(
        ListArtistExhibitsQuery(artist_id=current_user.user_id, page=page, size=size)
    )
    return PageResponse[AdminExhibitListItemResponse].of(
        result,
        items=[to_list_item_response(item) for item in result.items],
    )


@router.put(
    "/{exhibit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=error_responses(
        *AUTHENTICATION_ERRORS,
        UserError.artist_role_required,
        ExhibitError.not_found,
        ExhibitError.title_required,
        ExhibitError.invalid_schedule,
        ExhibitError.hall_name_required,
        ExhibitError.invalid_coordinates,
        ExhibitError.domestic_mismatch,
        ExhibitError.unknown_country,
        ExhibitError.unknown_keyword,
    ),
)
def update_artist_exhibit(
    exhibit_id: ExhibitIdParam,
    body: CreateExhibitRequest,
    current_user: CurrentUserDep,
    use_case: UpdateArtistExhibitUseCaseDep,
) -> None:
    use_case.update_artist_exhibit(
        UpdateArtistExhibitCommand(
            artist_id=current_user.user_id,
            exhibit_id=exhibit_id,
            exhibit=body.to_command(),
        )
    )


@router.delete(
    "/{exhibit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=error_responses(
        *AUTHENTICATION_ERRORS,
        UserError.artist_role_required,
        ExhibitError.not_found,
    ),
)
def delete_artist_exhibit(
    exhibit_id: ExhibitIdParam,
    current_user: CurrentUserDep,
    use_case: DeleteArtistExhibitUseCaseDep,
) -> None:
    use_case.delete_artist_exhibit(
        DeleteArtistExhibitCommand(
            artist_id=current_user.user_id, exhibit_id=exhibit_id
        )
    )
