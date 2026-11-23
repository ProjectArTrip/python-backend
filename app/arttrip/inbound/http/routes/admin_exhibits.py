from datetime import date
from typing import Annotated, Final

from fastapi import APIRouter, Path, Query

from arttrip.application.domain.exhibit.exceptions import ExhibitError
from arttrip.application.domain.exhibit.exhibit_filter import ExhibitFilter
from arttrip.application.domain.exhibit.exhibit_search import (
    ExhibitSearch,
    ExhibitSortField,
)
from arttrip.application.port.input.exhibit.commands import (
    UpdateExhibitCommand,
)
from arttrip.application.port.input.exhibit.queries import SearchExhibitsQuery
from arttrip.application.port.input.exhibit.results import ExhibitSearchItem
from arttrip.inbound.http.dependencies.exhibit import (
    CreateExhibitUseCaseDep,
    DeleteExhibitUseCaseDep,
    GetManagedExhibitUseCaseDep,
    SearchExhibitsUseCaseDep,
    UpdateExhibitUseCaseDep,
)
from arttrip.inbound.http.openapi import ADMIN_ERRORS, error_responses
from arttrip.inbound.http.schemas.admin_exhibits import (
    AdminExhibitDetailResponse,
    AdminExhibitListItemResponse,
    AdminExhibitSearchParams,
    CreateExhibitRequest,
    ExhibitCreatedResponse,
    UpdateExhibitRequest,
)
from arttrip.inbound.http.schemas.base import PageResponse

router = APIRouter()

_SORT_FIELDS: Final[dict[str, ExhibitSortField]] = {
    "createdAt": ExhibitSortField.CREATED_AT,
    "startDate": ExhibitSortField.START_DATE,
    "endDate": ExhibitSortField.END_DATE,
    "title": ExhibitSortField.TITLE,
}

PERIOD_DATE_FORMAT: Final = "%Y.%m.%d"
ALWAYS_OPEN_LABEL: Final = "상시 진행중"

ExhibitIdParam = Annotated[int, Path(gt=0)]


@router.get(
    "",
    response_model=PageResponse[AdminExhibitListItemResponse],
    responses=error_responses(
        *ADMIN_ERRORS, ExhibitError.invalid_period, ExhibitError.unknown_country
    ),
)
def search_exhibits(
    use_case: SearchExhibitsUseCaseDep,
    params: Annotated[AdminExhibitSearchParams, Query()],
) -> PageResponse[AdminExhibitListItemResponse]:
    search_text = params.keyword.strip() if params.keyword is not None else ""
    result = use_case.search_exhibits(
        SearchExhibitsQuery(
            search=ExhibitSearch(
                criteria=ExhibitFilter(
                    search_text=search_text or None,
                    period_start=params.start_date,
                    period_end=params.end_date,
                    regions=(
                        frozenset({params.region}) if params.region else frozenset()
                    ),
                ),
                statuses=frozenset(params.status or ()),
                genre_names=frozenset(params.genre or ()),
            ),
            country_name=params.country or None,
            sort=_SORT_FIELDS[params.sort],
            direction=params.direction,
            page=params.page,
            size=params.size,
        )
    )
    return PageResponse[AdminExhibitListItemResponse].of(
        result,
        items=[
            AdminExhibitListItemResponse(
                exhibit_id=item.exhibit_id,
                title=item.title,
                exhibit_period=_format_period(item.start_date, item.end_date),
                country=item.country_name,
                region=item.region,
                genres=list(item.genres),
                status=item.status,
                hall_name=item.hall_name,
            )
            for item in result.items
        ],
    )


@router.post(
    "",
    status_code=201,
    response_model=ExhibitCreatedResponse,
    responses=error_responses(
        *ADMIN_ERRORS,
        ExhibitError.title_required,
        ExhibitError.invalid_schedule,
        ExhibitError.hall_name_required,
        ExhibitError.invalid_coordinates,
        ExhibitError.domestic_mismatch,
        ExhibitError.unknown_keyword,
        ExhibitError.duplicate,
    ),
)
def create_exhibit(
    body: CreateExhibitRequest,
    use_case: CreateExhibitUseCaseDep,
) -> ExhibitCreatedResponse:
    exhibit_id = use_case.create_exhibit(body.to_command())
    return ExhibitCreatedResponse(exhibit_id=exhibit_id)


@router.get(
    "/{exhibit_id}",
    response_model=AdminExhibitDetailResponse,
    responses=error_responses(*ADMIN_ERRORS, ExhibitError.not_found),
)
def get_managed_exhibit(
    exhibit_id: ExhibitIdParam,
    use_case: GetManagedExhibitUseCaseDep,
) -> AdminExhibitDetailResponse:
    exhibit = use_case.get_managed_exhibit(exhibit_id)
    return AdminExhibitDetailResponse(
        exhibit_id=exhibit.exhibit_id,
        title=exhibit.title,
        description=exhibit.description,
        poster_url=exhibit.poster_url,
        ticket_url=exhibit.ticket_url,
        start_date=exhibit.start_date,
        end_date=exhibit.end_date,
        status=exhibit.status,
        exhibit_hall_id=exhibit.hall_id,
        exhibit_hall_name=exhibit.hall_name,
        country=exhibit.country_name,
        region=exhibit.region,
        address=exhibit.address,
        opening_hours=exhibit.opening_hours,
        phone=exhibit.phone,
        latitude=float(exhibit.latitude),
        longitude=float(exhibit.longitude),
        is_domestic=exhibit.is_domestic,
        genres=list(exhibit.genres),
        styles=list(exhibit.styles),
    )


@router.put(
    "/{exhibit_id}",
    status_code=204,
    responses=error_responses(
        *ADMIN_ERRORS,
        ExhibitError.not_found,
        ExhibitError.title_required,
        ExhibitError.invalid_schedule,
        ExhibitError.hall_name_required,
        ExhibitError.invalid_coordinates,
        ExhibitError.unknown_country,
        ExhibitError.unknown_keyword,
        ExhibitError.domestic_mismatch,
    ),
)
def update_exhibit(
    exhibit_id: ExhibitIdParam,
    body: UpdateExhibitRequest,
    use_case: UpdateExhibitUseCaseDep,
) -> None:
    use_case.update_exhibit(
        UpdateExhibitCommand(
            exhibit_id=exhibit_id,
            title=body.title,
            description=body.description,
            poster_url=body.poster_url,
            ticket_url=body.ticket_url,
            start_date=body.start_date,
            end_date=body.end_date,
            hall_name=body.exhibit_hall_name,
            country_name=body.country,
            region=body.region,
            address=body.address,
            opening_hours=body.opening_hours,
            phone=body.phone,
            latitude=body.latitude,
            longitude=body.longitude,
            genre_names=frozenset(body.genres),
            style_names=frozenset(body.styles),
            is_domestic=body.is_domestic,
        )
    )


@router.delete(
    "/{exhibit_id}",
    status_code=204,
    responses=error_responses(*ADMIN_ERRORS, ExhibitError.not_found),
)
def delete_exhibit(
    exhibit_id: ExhibitIdParam,
    use_case: DeleteExhibitUseCaseDep,
) -> None:
    use_case.delete_exhibit(exhibit_id)


# 레거시 인용이기 때문에 소비되는곳 확인 후 리팩토링 진행
def _format_period(start: date | None, end: date | None) -> str:
    if start is None and end is None:
        return ALWAYS_OPEN_LABEL
    if end is None and start is not None:
        return f"{start.strftime(PERIOD_DATE_FORMAT)} -"
    if start is None and end is not None:
        return end.strftime(PERIOD_DATE_FORMAT)
    assert start is not None and end is not None
    return f"{start.strftime(PERIOD_DATE_FORMAT)} - {end.strftime(PERIOD_DATE_FORMAT)}"


def to_list_item_response(item: ExhibitSearchItem) -> AdminExhibitListItemResponse:
    return AdminExhibitListItemResponse(
        exhibit_id=item.exhibit_id,
        title=item.title,
        exhibit_period=_format_period(item.start_date, item.end_date),
        country=item.country_name,
        region=item.region,
        genres=list(item.genres),
        status=item.status,
        hall_name=item.hall_name,
    )
