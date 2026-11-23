from typing import Annotated

from fastapi import APIRouter, Path, Query

from arttrip.application.domain.curation.exceptions import CurationError
from arttrip.application.port.input.curation.queries import (
    GetCurationQuery,
    PickCurationQuery,
)
from arttrip.inbound.http.dependencies.auth import OptionalUserDep
from arttrip.inbound.http.dependencies.curation import (
    GetCurationUseCaseDep,
    PickCurationUseCaseDep,
)
from arttrip.inbound.http.openapi import AUTHENTICATION_ERRORS, error_responses
from arttrip.inbound.http.pagination import DEFAULT_PAGE_SIZE, PageSizeParam
from arttrip.inbound.http.routes.exhibits import to_exhibit_summary_response
from arttrip.inbound.http.schemas.curations import (
    CurationDetailResponse,
    CurationSummaryResponse,
)

router = APIRouter()

DisplayOrderCursorParam = Annotated[int | None, Query(alias="cursor", ge=0)]


@router.get(
    "/{curation_id}",
    response_model=CurationDetailResponse,
    responses=error_responses(*AUTHENTICATION_ERRORS, CurationError.not_found),
)
def get_curation(
    curation_id: Annotated[int, Path(gt=0)],
    current_user: OptionalUserDep,
    use_case: GetCurationUseCaseDep,
    cursor: DisplayOrderCursorParam = None,
    size: PageSizeParam = DEFAULT_PAGE_SIZE,
) -> CurationDetailResponse:
    curation = use_case.get_curation(
        GetCurationQuery(
            user_id=current_user.user_id if current_user is not None else None,
            curation_id=curation_id,
            cursor=cursor,
            size=size,
        )
    )
    return CurationDetailResponse(
        id=curation.curation_id,
        title=curation.title,
        exhibits=[to_exhibit_summary_response(item) for item in curation.page.items],
        next_cursor=curation.page.next_cursor,
        has_next=curation.page.has_next,
    )


@router.get(
    "",
    response_model=CurationSummaryResponse,
    responses=error_responses(*AUTHENTICATION_ERRORS, CurationError.not_found),
)
def pick_curation(
    current_user: OptionalUserDep,
    use_case: PickCurationUseCaseDep,
    domestic: bool | None = None,
    country_code: Annotated[
        str | None, Query(alias="countryCode", pattern="^[A-Za-z]{2}$")
    ] = None,
) -> CurationSummaryResponse:
    curation = use_case.pick_curation(
        PickCurationQuery(
            user_id=current_user.user_id if current_user is not None else None,
            domestic=domestic,
            country_code=country_code.upper() if country_code is not None else None,
        )
    )
    return CurationSummaryResponse(
        id=curation.curation_id,
        title=curation.title,
        exhibits=[to_exhibit_summary_response(item) for item in curation.exhibits],
    )
