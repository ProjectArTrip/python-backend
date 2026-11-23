from fastapi import APIRouter

from arttrip.application.port.input.exhibit.queries import ListRecentExhibitsQuery
from arttrip.inbound.http.dependencies.auth import CurrentUserDep
from arttrip.inbound.http.dependencies.exhibit import ListRecentExhibitsUseCaseDep
from arttrip.inbound.http.openapi import AUTHENTICATION_ERRORS, error_responses
from arttrip.inbound.http.routes.exhibits import to_exhibit_summary_response
from arttrip.inbound.http.schemas.exhibits import RecentExhibitListResponse

router = APIRouter()


@router.get(
    "",
    response_model=RecentExhibitListResponse,
    responses=error_responses(*AUTHENTICATION_ERRORS),
)
def list_recent_exhibits(
    current_user: CurrentUserDep,
    use_case: ListRecentExhibitsUseCaseDep,
) -> RecentExhibitListResponse:
    exhibits = use_case.list_recent_exhibits(
        ListRecentExhibitsQuery(user_id=current_user.user_id)
    )
    return RecentExhibitListResponse(
        exhibits=[to_exhibit_summary_response(exhibit) for exhibit in exhibits]
    )
