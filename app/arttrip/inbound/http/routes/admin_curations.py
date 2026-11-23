from typing import Annotated

from fastapi import APIRouter, Path

from arttrip.application.domain.curation.exceptions import CurationError
from arttrip.application.port.input.curation.commands import (
    CreateCurationCommand,
    UpdateCurationCommand,
)
from arttrip.application.port.input.curation.queries import SearchCurationsQuery
from arttrip.inbound.http.dependencies.curation import (
    CreateCurationUseCaseDep,
    DeleteCurationUseCaseDep,
    GetManagedCurationUseCaseDep,
    SearchCurationsUseCaseDep,
    UpdateCurationUseCaseDep,
)
from arttrip.inbound.http.openapi import ADMIN_ERRORS, error_responses
from arttrip.inbound.http.pagination import (
    DEFAULT_PAGE_SIZE,
    AdminPageSizeParam,
    PageIndexParam,
)
from arttrip.inbound.http.query_params import SearchTextParam
from arttrip.inbound.http.schemas.admin_curations import (
    AdminCurationCreatedResponse,
    AdminCurationDetailResponse,
    AdminCurationExhibitResponse,
    AdminCurationListItemResponse,
    CurationFormRequest,
)
from arttrip.inbound.http.schemas.base import PageResponse

router = APIRouter()

CurationIdParam = Annotated[int, Path(gt=0)]


@router.get(
    "",
    response_model=PageResponse,
    responses=error_responses(*ADMIN_ERRORS),
)
def search_curations(
    use_case: SearchCurationsUseCaseDep,
    page: PageIndexParam = 0,
    size: AdminPageSizeParam = DEFAULT_PAGE_SIZE,
    keyword: SearchTextParam = None,
    active: bool | None = None,
) -> PageResponse[AdminCurationListItemResponse]:
    search_text = keyword.strip() if keyword is not None else ""
    result = use_case.search_curations(
        SearchCurationsQuery(
            keyword=search_text or None, active=active, page=page, size=size
        )
    )
    return PageResponse[AdminCurationListItemResponse].of(
        result,
        items=[
            AdminCurationListItemResponse(
                curation_id=item.curation_id,
                title=item.title,
                exhibit_count=item.exhibit_count,
                created_at=item.created_at,
                visible_from=item.visible_from,
                visible_to=item.visible_to,
                active=item.active,
            )
            for item in result.items
        ],
    )


@router.get(
    "/{curation_id}",
    response_model=AdminCurationDetailResponse,
    responses=error_responses(*ADMIN_ERRORS, CurationError.not_found),
)
def get_managed_curation(
    curation_id: CurationIdParam,
    use_case: GetManagedCurationUseCaseDep,
) -> AdminCurationDetailResponse:
    curation = use_case.get_managed_curation(curation_id)
    return AdminCurationDetailResponse(
        curation_id=curation.curation_id,
        title=curation.title,
        refresh_cycle=curation.refresh_cycle,
        sort_type=curation.sort_type,
        visible_from=curation.visible_from,
        visible_to=curation.visible_to,
        active=curation.active,
        exhibits=[
            AdminCurationExhibitResponse(
                exhibit_id=exhibit.exhibit_id,
                title=exhibit.title,
                poster_url=exhibit.poster_url,
                status=exhibit.status,
                start_date=exhibit.start_date,
                end_date=exhibit.end_date,
                hall_name=exhibit.hall_name,
            )
            for exhibit in curation.exhibits
        ],
    )


@router.post(
    "",
    status_code=201,
    response_model=AdminCurationCreatedResponse,
    responses=error_responses(
        *ADMIN_ERRORS,
        CurationError.title_required,
        CurationError.invalid_period,
        CurationError.exhibits_required,
        CurationError.duplicate_exhibit,
        CurationError.unknown_exhibit,
    ),
)
def create_curation(
    body: CurationFormRequest,
    use_case: CreateCurationUseCaseDep,
) -> AdminCurationCreatedResponse:
    curation_id = use_case.create_curation(
        CreateCurationCommand(
            title=body.title,
            refresh_cycle=body.refresh_cycle,
            sort_type=body.sort_type,
            visible_from=body.visible_from,
            visible_to=body.visible_to,
            active=body.active,
            exhibit_ids=tuple(body.exhibit_ids),
        )
    )
    return AdminCurationCreatedResponse(curation_id=curation_id)


@router.patch(
    "/{curation_id}",
    status_code=204,
    responses=error_responses(
        *ADMIN_ERRORS,
        CurationError.not_found,
        CurationError.title_required,
        CurationError.invalid_period,
        CurationError.exhibits_required,
        CurationError.duplicate_exhibit,
        CurationError.unknown_exhibit,
    ),
)
def update_curation(
    curation_id: CurationIdParam,
    body: CurationFormRequest,
    use_case: UpdateCurationUseCaseDep,
) -> None:
    use_case.update_curation(
        UpdateCurationCommand(
            curation_id=curation_id,
            title=body.title,
            refresh_cycle=body.refresh_cycle,
            sort_type=body.sort_type,
            visible_from=body.visible_from,
            visible_to=body.visible_to,
            active=body.active,
            exhibit_ids=tuple(body.exhibit_ids),
        )
    )


@router.delete(
    "/{curation_id}",
    status_code=204,
    responses=error_responses(*ADMIN_ERRORS, CurationError.not_found),
)
def delete_curation(
    curation_id: CurationIdParam,
    use_case: DeleteCurationUseCaseDep,
) -> None:
    use_case.delete_curation(curation_id)
