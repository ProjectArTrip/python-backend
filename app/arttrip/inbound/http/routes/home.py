from typing import Annotated

from fastapi import APIRouter, Query

from arttrip.application.port.input.home.queries import (
    ListGenreExhibitsQuery,
    ListPersonalizedExhibitsQuery,
    ListScheduledExhibitsQuery,
    ListTodayExhibitsQuery,
)
from arttrip.inbound.http.dependencies.auth import CurrentUserDep, OptionalUserDep
from arttrip.inbound.http.dependencies.home import (
    ListGenreExhibitsUseCaseDep,
    ListPersonalizedExhibitsUseCaseDep,
    ListScheduledExhibitsUseCaseDep,
    ListTodayExhibitsUseCaseDep,
)
from arttrip.inbound.http.openapi import AUTHENTICATION_ERRORS, error_responses
from arttrip.inbound.http.routes.exhibits import to_exhibit_summary_response
from arttrip.inbound.http.schemas.home import (
    HomeExhibitListResponse,
    HomeGenreParams,
    HomeLocationParams,
    HomeScheduleParams,
)

router = APIRouter()


@router.get(
    "/today",
    response_model=HomeExhibitListResponse,
    responses=error_responses(*AUTHENTICATION_ERRORS),
)
def list_today_exhibits(
    current_user: OptionalUserDep,
    use_case: ListTodayExhibitsUseCaseDep,
    params: Annotated[HomeLocationParams, Query()],
) -> HomeExhibitListResponse:
    exhibits = use_case.list_today_exhibits(
        ListTodayExhibitsQuery(
            user_id=current_user.user_id if current_user is not None else None,
            domestic=params.domestic,
            country_code=(
                params.country_code.upper() if params.country_code is not None else None
            ),
            region=params.region,
        )
    )
    return HomeExhibitListResponse(
        exhibits=[to_exhibit_summary_response(exhibit) for exhibit in exhibits]
    )


@router.get(
    "/schedule",
    response_model=HomeExhibitListResponse,
    responses=error_responses(*AUTHENTICATION_ERRORS),
)
def list_scheduled_exhibits(
    current_user: OptionalUserDep,
    use_case: ListScheduledExhibitsUseCaseDep,
    params: Annotated[HomeScheduleParams, Query()],
) -> HomeExhibitListResponse:
    exhibits = use_case.list_scheduled_exhibits(
        ListScheduledExhibitsQuery(
            user_id=current_user.user_id if current_user is not None else None,
            scheduled_date=params.scheduled_date,
            domestic=params.domestic,
            country_code=(
                params.country_code.upper() if params.country_code is not None else None
            ),
            region=params.region,
        )
    )
    return HomeExhibitListResponse(
        exhibits=[to_exhibit_summary_response(exhibit) for exhibit in exhibits]
    )


@router.get(
    "/personalized",
    response_model=HomeExhibitListResponse,
    responses=error_responses(*AUTHENTICATION_ERRORS),
)
def list_personalized_exhibits(
    current_user: CurrentUserDep,
    use_case: ListPersonalizedExhibitsUseCaseDep,
    params: Annotated[HomeLocationParams, Query()],
) -> HomeExhibitListResponse:
    exhibits = use_case.list_personalized_exhibits(
        ListPersonalizedExhibitsQuery(
            user_id=current_user.user_id,
            domestic=params.domestic,
            country_code=(
                params.country_code.upper() if params.country_code is not None else None
            ),
            region=params.region,
        )
    )
    return HomeExhibitListResponse(
        exhibits=[to_exhibit_summary_response(exhibit) for exhibit in exhibits]
    )


@router.get(
    "/genres",
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
