from typing import Annotated

from fastapi import APIRouter, Query

from arttrip.application.port.input.home.queries import (
    ListGenreExhibitsQuery,
    ListTodayExhibitsQuery,
)
from arttrip.inbound.http.dependencies.auth import OptionalUserDep
from arttrip.inbound.http.dependencies.home import (
    ListGenreExhibitsUseCaseDep,
    ListHomeVenuesUseCaseDep,
    ListTodayExhibitsUseCaseDep,
)
from arttrip.inbound.http.openapi import AUTHENTICATION_ERRORS, error_responses
from arttrip.inbound.http.routes.exhibits import to_exhibit_summary_response
from arttrip.inbound.http.schemas.home import (
    HomeExhibitListResponse,
    HomeGenreParams,
    HomeVenueListResponse,
    HomeVenueResponse,
)

router = APIRouter()


@router.get(
    "/exhibits/today",
    response_model=HomeExhibitListResponse,
    responses=error_responses(*AUTHENTICATION_ERRORS),
)
def list_today_exhibits(
    current_user: OptionalUserDep,
    use_case: ListTodayExhibitsUseCaseDep,
) -> HomeExhibitListResponse:

    exhibits = use_case.list_today_exhibits(
        ListTodayExhibitsQuery(
            user_id=current_user.user_id if current_user is not None else None,
        )
    )

    return HomeExhibitListResponse(
        exhibits=[to_exhibit_summary_response(exhibit) for exhibit in exhibits]
    )


@router.get(
    "/exhibits/genres",
    response_model=HomeExhibitListResponse,
    responses=error_responses(*AUTHENTICATION_ERRORS),
)
def list_genre_exhibits(
    current_user: OptionalUserDep,
    use_case: ListGenreExhibitsUseCaseDep,
    params: Annotated[HomeGenreParams, Query()],
) -> HomeExhibitListResponse:
    exhibits = use_case.list_genre_exhibits(
        ListGenreExhibitsQuery(
            user_id=current_user.user_id if current_user is not None else None,
            genre_id=params.genre_id,
        )
    )
    return HomeExhibitListResponse(
        exhibits=[to_exhibit_summary_response(exhibit) for exhibit in exhibits]
    )


@router.get("/venues", response_model=HomeVenueListResponse)
def list_home_venues(use_case: ListHomeVenuesUseCaseDep) -> HomeVenueListResponse:
    venues = use_case.list_home_venues()
    return HomeVenueListResponse(
        venues=[
            HomeVenueResponse(
                venue_id=venue.venue_id,
                name=venue.name,
                region=venue.region,
                latitude=float(venue.latitude),
                longitude=float(venue.longitude),
                ongoing_exhibit_count=venue.ongoing_exhibit_count,
            )
            for venue in venues
        ]
    )
