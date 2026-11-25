import base64
import binascii
import json
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Path, Query

from arttrip.application.domain.exhibit.exceptions import ExhibitError
from arttrip.application.domain.exhibit.exhibit_filter import ExhibitFilter
from arttrip.application.domain.exhibit.exhibit_list_sort import (
    ExhibitListCursor,
    ExhibitListSort,
)
from arttrip.application.port.input.exhibit.queries import (
    GetExhibitQuery,
    ListExhibitsQuery,
)
from arttrip.application.port.input.exhibit.results import ExhibitSummary
from arttrip.inbound.http.dependencies.auth import CurrentUserDep
from arttrip.inbound.http.dependencies.exhibit import (
    GetExhibitUseCaseDep,
    ListExhibitsUseCaseDep,
)
from arttrip.inbound.http.dependencies.location import (
    ListDomesticRegionsUseCaseDep,
    ListOverseasCountriesUseCaseDep,
)
from arttrip.inbound.http.openapi import AUTHENTICATION_ERRORS, error_responses
from arttrip.inbound.http.schemas.exhibits import (
    CountryListResponse,
    CountryResponse,
    ExhibitDetailResponse,
    ExhibitHallResponse,
    ExhibitHallSummaryResponse,
    ExhibitListParams,
    ExhibitListResponse,
    ExhibitSummaryResponse,
    RegionListResponse,
    RegionResponse,
)

router = APIRouter()


@router.get("/countries", response_model=CountryListResponse)
def list_countries(use_case: ListOverseasCountriesUseCaseDep) -> CountryListResponse:
    return CountryListResponse(
        countries=[
            CountryResponse(country_code=country.code, name=country.name)
            for country in use_case.list_overseas_countries()
        ]
    )


@router.get("/regions", response_model=RegionListResponse)
def list_regions(use_case: ListDomesticRegionsUseCaseDep) -> RegionListResponse:
    return RegionListResponse(
        regions=[
            RegionResponse(region=region.name, image_url=region.image_url)
            for region in use_case.list_domestic_regions()
        ]
    )


@router.get(
    "/{exhibit_id}",
    response_model=ExhibitDetailResponse,
    responses=error_responses(*AUTHENTICATION_ERRORS, ExhibitError.not_found),
)
def get_exhibit(
    exhibit_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUserDep,
    use_case: GetExhibitUseCaseDep,
) -> ExhibitDetailResponse:
    exhibit = use_case.get_exhibit(
        GetExhibitQuery(user_id=current_user.user_id, exhibit_id=exhibit_id)
    )
    hall = exhibit.hall
    return ExhibitDetailResponse(
        exhibit_id=exhibit.exhibit_id,
        title=exhibit.title,
        description=exhibit.description,
        poster_url=exhibit.poster_url,
        ticket_url=exhibit.ticket_url,
        status=exhibit.status,
        start_date=exhibit.start_date,
        end_date=exhibit.end_date,
        hall=ExhibitHallResponse(
            name=hall.name,
            address=hall.address,
            phone=hall.phone,
            homepage_url=hall.homepage_url,
            opening_hours=hall.opening_hours,
            closed_days=hall.closed_days,
            region=hall.region,
            country_code=hall.country_code,
            latitude=float(hall.latitude),
            longitude=float(hall.longitude),
        ),
        is_favorite=exhibit.is_favorite,
        review_count=exhibit.review_count,
    )


@router.get(
    "",
    response_model=ExhibitListResponse,
    responses=error_responses(*AUTHENTICATION_ERRORS, ExhibitError.invalid_period),
)
def list_exhibits(
    current_user: CurrentUserDep,
    use_case: ListExhibitsUseCaseDep,
    params: Annotated[ExhibitListParams, Query()],
) -> ExhibitListResponse:
    search_text = params.q.strip() if params.q is not None else ""
    criteria = ExhibitFilter(
        search_text=search_text or None,
        period_start=params.start_date,
        period_end=params.end_date,
        domestic=params.domestic,
        country_code=(
            params.country_code.upper() if params.country_code is not None else None
        ),
        regions=frozenset(params.region or ()),
        genre_ids=frozenset(params.genre_ids or ()),
        style_ids=frozenset(params.style_ids or ()),
    )
    page = use_case.list_exhibits(
        ListExhibitsQuery(
            user_id=current_user.user_id,
            criteria=criteria,
            sort=params.sort,
            cursor=(
                _decode_cursor(params.cursor, params.sort)
                if params.cursor is not None
                else None
            ),
            size=params.size,
        )
    )
    return ExhibitListResponse(
        exhibits=[to_exhibit_summary_response(exhibit) for exhibit in page.items],
        next_cursor=_encode_cursor(page.next_cursor) if page.next_cursor else None,
        has_next=page.has_next,
    )


def to_exhibit_summary_response(exhibit: ExhibitSummary) -> ExhibitSummaryResponse:
    return ExhibitSummaryResponse(
        exhibit_id=exhibit.exhibit_id,
        title=exhibit.title,
        poster_url=exhibit.poster_url,
        status=exhibit.status,
        start_date=exhibit.start_date,
        end_date=exhibit.end_date,
        hall=ExhibitHallSummaryResponse(
            name=exhibit.hall.name,
            region=exhibit.hall.region,
            country_code=exhibit.hall.country_code,
        ),
        is_favorite=exhibit.is_favorite,
        genres=list(exhibit.genres),
    )


def _encode_cursor(cursor: ExhibitListCursor) -> str:
    value = cursor.value.isoformat() if isinstance(cursor.value, date) else cursor.value
    raw = json.dumps([cursor.sort, value, cursor.exhibit_id])
    return base64.urlsafe_b64encode(raw.encode()).decode()


def _decode_cursor(token: str, sort: ExhibitListSort) -> ExhibitListCursor:
    try:
        sort_name, value, exhibit_id = json.loads(base64.urlsafe_b64decode(token))
        if sort_name != sort or not isinstance(exhibit_id, int) or exhibit_id < 1:
            raise ValueError(token)
        if sort is ExhibitListSort.ENDING_SOON:
            return ExhibitListCursor(
                sort=sort, value=date.fromisoformat(value), exhibit_id=exhibit_id
            )
        if not isinstance(value, int):
            raise ValueError(token)
        return ExhibitListCursor(sort=sort, value=value, exhibit_id=exhibit_id)
    except (binascii.Error, ValueError, TypeError) as error:
        raise ExhibitError.invalid_cursor() from error
