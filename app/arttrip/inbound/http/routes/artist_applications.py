from fastapi import APIRouter, status

from arttrip.application.domain.artist_application.exceptions import (
    ArtistApplicationError,
)
from arttrip.application.domain.user.exceptions import UserError
from arttrip.application.port.input.artist_application.commands import (
    SubmitArtistApplicationCommand,
)
from arttrip.application.port.input.artist_application.results import (
    ArtistApplicationView,
)
from arttrip.inbound.http.dependencies.artist_application import (
    GetLatestArtistApplicationUseCaseDep,
    SubmitArtistApplicationUseCaseDep,
)
from arttrip.inbound.http.dependencies.auth import CurrentUserDep
from arttrip.inbound.http.openapi import AUTHENTICATION_ERRORS, error_responses
from arttrip.inbound.http.schemas.artist_applications import (
    ArtistApplicationResponse,
    SubmitArtistApplicationRequest,
    SubmitArtistApplicationResponse,
)

router = APIRouter()


@router.post(
    "",
    response_model=SubmitArtistApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    responses=error_responses(
        *AUTHENTICATION_ERRORS,
        UserError.artist_verification_not_allowed,
        ArtistApplicationError.already_pending,
        ArtistApplicationError.invalid_introduction,
        ArtistApplicationError.invalid_portfolio_url,
    ),
)
def submit_artist_application(
    body: SubmitArtistApplicationRequest,
    current_user: CurrentUserDep,
    use_case: SubmitArtistApplicationUseCaseDep,
) -> SubmitArtistApplicationResponse:
    result = use_case.submit_artist_application(
        SubmitArtistApplicationCommand(
            user_id=current_user.user_id,
            introduction=body.introduction,
            portfolio_url=body.portfolio_url,
        )
    )
    application = result.application
    return SubmitArtistApplicationResponse(
        id=application.application_id,
        status=application.status,
        introduction=application.introduction,
        portfolio_url=application.portfolio_url,
        rejection_reason=application.rejection_reason,
        submitted_at=application.submitted_at,
        reviewed_at=application.reviewed_at,
        onboarding_step=result.onboarding_step,
    )


@router.get(
    "",
    response_model=ArtistApplicationResponse,
    responses=error_responses(*AUTHENTICATION_ERRORS, ArtistApplicationError.not_found),
)
def get_latest_artist_application(
    current_user: CurrentUserDep,
    use_case: GetLatestArtistApplicationUseCaseDep,
) -> ArtistApplicationResponse:
    return _to_response(use_case.get_latest_artist_application(current_user.user_id))


def _to_response(application: ArtistApplicationView) -> ArtistApplicationResponse:
    return ArtistApplicationResponse(
        id=application.application_id,
        status=application.status,
        introduction=application.introduction,
        portfolio_url=application.portfolio_url,
        rejection_reason=application.rejection_reason,
        submitted_at=application.submitted_at,
        reviewed_at=application.reviewed_at,
    )
