from typing import Annotated

from fastapi import APIRouter, Path

from arttrip.application.domain.artist_application.artist_application_status import (
    ArtistApplicationStatus,
)
from arttrip.application.domain.artist_application.exceptions import (
    ArtistApplicationError,
)
from arttrip.application.domain.user.exceptions import UserError
from arttrip.application.port.input.artist_application.commands import (
    ApproveArtistApplicationCommand,
    RejectArtistApplicationCommand,
)
from arttrip.application.port.input.artist_application.queries import (
    ListArtistApplicationsQuery,
)
from arttrip.application.port.input.artist_application.results import (
    ArtistApplicationView,
    ManagedArtistApplication,
)
from arttrip.inbound.http.dependencies.artist_application import (
    ApproveArtistApplicationUseCaseDep,
    GetManagedArtistApplicationUseCaseDep,
    ListArtistApplicationsUseCaseDep,
    RejectArtistApplicationUseCaseDep,
)
from arttrip.inbound.http.dependencies.auth import AdminUserDep
from arttrip.inbound.http.openapi import ADMIN_ERRORS, error_responses
from arttrip.inbound.http.pagination import (
    DEFAULT_PAGE_SIZE,
    CursorParam,
    PageSizeParam,
)
from arttrip.inbound.http.schemas.admin_artist_applications import (
    AdminArtistApplicationDetailResponse,
    AdminArtistApplicationListResponse,
    AdminArtistApplicationResponse,
    ApplicantResponse,
    RejectArtistApplicationRequest,
)
from arttrip.inbound.http.schemas.base import CaseInsensitive

router = APIRouter()

ApplicationIdParam = Annotated[int, Path(gt=0)]
StatusParam = Annotated[ArtistApplicationStatus | None, CaseInsensitive]


@router.get(
    "",
    response_model=AdminArtistApplicationListResponse,
    responses=error_responses(*ADMIN_ERRORS),
)
def list_artist_applications(
    use_case: ListArtistApplicationsUseCaseDep,
    status: StatusParam = None,
    cursor: CursorParam = None,
    size: PageSizeParam = DEFAULT_PAGE_SIZE,
) -> AdminArtistApplicationListResponse:
    page = use_case.list_artist_applications(
        ListArtistApplicationsQuery(status=status, cursor=cursor, size=size)
    )
    return AdminArtistApplicationListResponse(
        requests=[_to_response(item) for item in page.items],
        next_cursor=page.next_cursor,
        has_next=page.has_next,
    )


@router.post(
    "/{application_id}/approve",
    response_model=AdminArtistApplicationResponse,
    responses=error_responses(
        *ADMIN_ERRORS,
        ArtistApplicationError.not_found,
        ArtistApplicationError.already_reviewed,
        UserError.artist_verification_not_allowed,
    ),
)
def approve_artist_application(
    application_id: ApplicationIdParam,
    admin: AdminUserDep,
    use_case: ApproveArtistApplicationUseCaseDep,
) -> AdminArtistApplicationResponse:
    application = use_case.approve_artist_application(
        ApproveArtistApplicationCommand(
            application_id=application_id, reviewer_id=admin.user_id
        )
    )
    return _to_response(application)


@router.post(
    "/{application_id}/reject",
    response_model=AdminArtistApplicationResponse,
    responses=error_responses(
        *ADMIN_ERRORS,
        ArtistApplicationError.not_found,
        ArtistApplicationError.already_reviewed,
        ArtistApplicationError.rejection_reason_required,
    ),
)
@router.get(
    "/{application_id}",
    response_model=AdminArtistApplicationDetailResponse,
    responses=error_responses(*ADMIN_ERRORS, ArtistApplicationError.not_found),
)
def get_artist_application(
    application_id: ApplicationIdParam,
    use_case: GetManagedArtistApplicationUseCaseDep,
) -> AdminArtistApplicationDetailResponse:
    managed = use_case.get_managed_artist_application(application_id)
    return _to_detail_response(managed)


def reject_artist_application(
    application_id: ApplicationIdParam,
    body: RejectArtistApplicationRequest,
    admin: AdminUserDep,
    use_case: RejectArtistApplicationUseCaseDep,
) -> AdminArtistApplicationResponse:
    application = use_case.reject_artist_application(
        RejectArtistApplicationCommand(
            application_id=application_id,
            reviewer_id=admin.user_id,
            reason=body.reason,
        )
    )
    return _to_response(application)


def _to_response(application: ArtistApplicationView) -> AdminArtistApplicationResponse:
    return AdminArtistApplicationResponse(
        id=application.application_id,
        status=application.status,
        introduction=application.introduction,
        portfolio_url=application.portfolio_url,
        rejection_reason=application.rejection_reason,
        submitted_at=application.submitted_at,
        reviewed_at=application.reviewed_at,
    )


def _to_detail_response(
    managed: ManagedArtistApplication,
) -> AdminArtistApplicationDetailResponse:
    return AdminArtistApplicationDetailResponse(
        application=_to_response(managed.application),
        applicant=ApplicantResponse(
            id=managed.applicant_id, nickname=managed.applicant_nickname
        ),
        reviewed_by=managed.reviewed_by,
    )
