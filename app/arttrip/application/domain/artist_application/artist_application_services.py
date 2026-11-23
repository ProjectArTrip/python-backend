from datetime import UTC, datetime

from arttrip.application.domain.artist_application.artist_application import (
    ArtistApplication,
)
from arttrip.application.domain.artist_application.exceptions import (
    ArtistApplicationError,
)
from arttrip.application.domain.notification.notification import Notification
from arttrip.application.domain.user.current_user import load_current_user
from arttrip.application.domain.user.role import UserRole
from arttrip.application.port.input.artist_application.commands import (
    ApproveArtistApplicationCommand,
    RejectArtistApplicationCommand,
    SubmitArtistApplicationCommand,
)
from arttrip.application.port.input.artist_application.queries import (
    ListArtistApplicationsQuery,
)
from arttrip.application.port.input.artist_application.results import (
    ArtistApplicationView,
    ManagedArtistApplication,
    SubmitArtistApplicationResult,
)
from arttrip.application.port.input.artist_application.use_cases import (
    ApproveArtistApplicationUseCase,
    GetLatestArtistApplicationUseCase,
    GetManagedArtistApplicationUseCase,
    ListArtistApplicationsUseCase,
    RejectArtistApplicationUseCase,
    SubmitArtistApplicationUseCase,
)
from arttrip.application.port.input.pagination import CursorPage
from arttrip.application.port.output.unit_of_work import UnitOfWork


class SubmitArtistApplicationService(SubmitArtistApplicationUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def submit_artist_application(
        self, command: SubmitArtistApplicationCommand
    ) -> SubmitArtistApplicationResult:
        now = datetime.now(UTC)

        with self._uow as uow:
            user = load_current_user(uow.users, command.user_id)
            user.request_artist_verification(now=now)

            pending = uow.artist_applications.find_pending_by_user_id(command.user_id)
            if pending is not None:
                raise ArtistApplicationError.already_pending()

            application = ArtistApplication.submit(
                user_id=command.user_id,
                introduction=command.introduction,
                portfolio_url=command.portfolio_url,
                now=now,
            )
            uow.artist_applications.add(application)

            application_id = to_view(application).application_id
            admin_ids = uow.users.find_ids_by_role(UserRole.ADMIN)
            uow.notifications.add_all(
                [
                    Notification.artist_application_submitted(
                        admin_id=admin_id,
                        applicant_nickname=user.nickname,
                        application_id=application_id,
                        now=now,
                    )
                    for admin_id in admin_ids
                ]
            )
            return SubmitArtistApplicationResult(
                application=to_view(application),
                onboarding_step=user.onboarding_step,
            )


class GetLatestArtistApplicationService(GetLatestArtistApplicationUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def get_latest_artist_application(self, user_id: int) -> ArtistApplicationView:
        with self._uow as uow:
            application = uow.artist_applications.find_latest_by_user_id(user_id)
            if application is None:
                raise ArtistApplicationError.not_found()
            return to_view(application)


class ListArtistApplicationsService(ListArtistApplicationsUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def list_artist_applications(
        self, query: ListArtistApplicationsQuery
    ) -> CursorPage[ArtistApplicationView]:
        with self._uow as uow:
            rows = uow.artist_applications.list_page(
                status=query.status, cursor=query.cursor, limit=query.size + 1
            )
            has_next = len(rows) > query.size
            items = tuple(to_view(row) for row in rows[: query.size])
            next_cursor = items[-1].application_id if has_next else None
            return CursorPage(items=items, next_cursor=next_cursor)


class GetManagedArtistApplicationService(GetManagedArtistApplicationUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def get_managed_artist_application(
        self, application_id: int
    ) -> ManagedArtistApplication:
        with self._uow as uow:
            application = _load(uow, application_id)
            applicant = uow.users.find_by_id(application.user_id)
            if applicant is None:
                raise ArtistApplicationError.not_found()
            return ManagedArtistApplication(
                application=to_view(application),
                applicant_id=application.user_id,
                applicant_nickname=applicant.nickname,
                reviewed_by=application.reviewed_by,
            )


class ApproveArtistApplicationService(ApproveArtistApplicationUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def approve_artist_application(
        self, command: ApproveArtistApplicationCommand
    ) -> ArtistApplicationView:
        now = datetime.now(UTC)

        with self._uow as uow:
            application = _load(uow, command.application_id)
            application.approve(reviewer_id=command.reviewer_id, now=now)

            applicant = uow.users.find_by_id(application.user_id)
            if applicant is None:
                raise ArtistApplicationError.not_found()
            applicant.become_artist(now=now)
            uow.notifications.add_all(
                [
                    Notification.artist_application_approved(
                        applicant_id=application.user_id,
                        application_id=command.application_id,
                        now=now,
                    )
                ]
            )
            return to_view(application)


class RejectArtistApplicationService(RejectArtistApplicationUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def reject_artist_application(
        self, command: RejectArtistApplicationCommand
    ) -> ArtistApplicationView:
        now = datetime.now(UTC)
        with self._uow as uow:
            application = _load(uow, command.application_id)
            application.reject(
                reviewer_id=command.reviewer_id,
                reason=command.reason,
                now=datetime.now(UTC),
            )
            uow.notifications.add_all(
                [
                    Notification.artist_application_rejected(
                        applicant_id=application.user_id,
                        application_id=command.application_id,
                        now=now,
                    )
                ]
            )
            return to_view(application)


def to_view(application: ArtistApplication) -> ArtistApplicationView:
    application_id = application.id
    if application_id is None:
        raise RuntimeError("artist application must have an id after it is stored")
    return ArtistApplicationView(
        application_id=application_id,
        status=application.status,
        introduction=application.introduction,
        portfolio_url=application.portfolio_url,
        rejection_reason=application.rejection_reason,
        submitted_at=application.submitted_at,
        reviewed_at=application.reviewed_at,
    )


def _load(uow: UnitOfWork, application_id: int) -> ArtistApplication:
    application = uow.artist_applications.find_by_id(application_id)
    if application is None:
        raise ArtistApplicationError.not_found()
    return application
