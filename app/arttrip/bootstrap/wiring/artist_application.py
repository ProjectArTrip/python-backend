from fastapi import Request

from arttrip.application.domain.artist_application.artist_application_services import (
    ApproveArtistApplicationService,
    GetLatestArtistApplicationService,
    GetManagedArtistApplicationService,
    ListArtistApplicationsService,
    RejectArtistApplicationService,
    SubmitArtistApplicationService,
)
from arttrip.application.port.input.artist_application.use_cases import (
    ApproveArtistApplicationUseCase,
    GetLatestArtistApplicationUseCase,
    GetManagedArtistApplicationUseCase,
    ListArtistApplicationsUseCase,
    RejectArtistApplicationUseCase,
    SubmitArtistApplicationUseCase,
)
from arttrip.bootstrap.wiring.common import Overrides, new_unit_of_work
from arttrip.inbound.http.dependencies.artist_application import (
    provide_approve_artist_application_use_case,
    provide_get_latest_artist_application_use_case,
    provide_get_managed_artist_application_use_case,
    provide_list_artist_applications_use_case,
    provide_reject_artist_application_use_case,
    provide_submit_artist_application_use_case,
)


def build_submit_artist_application_use_case(
    request: Request,
) -> SubmitArtistApplicationUseCase:
    return SubmitArtistApplicationService(uow=new_unit_of_work(request))


def build_get_latest_artist_application_use_case(
    request: Request,
) -> GetLatestArtistApplicationUseCase:
    return GetLatestArtistApplicationService(uow=new_unit_of_work(request))


def build_list_artist_applications_use_case(
    request: Request,
) -> ListArtistApplicationsUseCase:
    return ListArtistApplicationsService(uow=new_unit_of_work(request))


def build_approve_artist_application_use_case(
    request: Request,
) -> ApproveArtistApplicationUseCase:
    return ApproveArtistApplicationService(uow=new_unit_of_work(request))


def build_reject_artist_application_use_case(
    request: Request,
) -> RejectArtistApplicationUseCase:
    return RejectArtistApplicationService(uow=new_unit_of_work(request))


def build_get_managed_artist_application_use_case(
    request: Request,
) -> GetManagedArtistApplicationUseCase:
    return GetManagedArtistApplicationService(uow=new_unit_of_work(request))


def wire_artist_application(overrides: Overrides) -> None:
    overrides[provide_submit_artist_application_use_case] = (
        build_submit_artist_application_use_case
    )
    overrides[provide_get_latest_artist_application_use_case] = (
        build_get_latest_artist_application_use_case
    )
    overrides[provide_list_artist_applications_use_case] = (
        build_list_artist_applications_use_case
    )
    overrides[provide_approve_artist_application_use_case] = (
        build_approve_artist_application_use_case
    )
    overrides[provide_reject_artist_application_use_case] = (
        build_reject_artist_application_use_case
    )
    overrides[provide_get_managed_artist_application_use_case] = (
        build_get_managed_artist_application_use_case
    )
