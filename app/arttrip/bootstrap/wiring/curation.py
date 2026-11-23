from fastapi import Request

from arttrip.application.domain.curation.curation_management_services import (
    CreateCurationService,
    DeleteCurationService,
    GetManagedCurationService,
    SearchCurationsService,
    UpdateCurationService,
)
from arttrip.application.domain.curation.curation_services import (
    GetCurationService,
    PickCurationService,
)
from arttrip.application.port.input.curation.use_cases import (
    CreateCurationUseCase,
    DeleteCurationUseCase,
    GetCurationUseCase,
    GetManagedCurationUseCase,
    PickCurationUseCase,
    SearchCurationsUseCase,
    UpdateCurationUseCase,
)
from arttrip.bootstrap.wiring.common import Overrides, new_unit_of_work
from arttrip.common import settings
from arttrip.inbound.http.dependencies.curation import (
    provide_create_curation_use_case,
    provide_delete_curation_use_case,
    provide_get_curation_use_case,
    provide_get_managed_curation_use_case,
    provide_pick_curation_use_case,
    provide_search_curations_use_case,
    provide_update_curation_use_case,
)


def build_get_curation_use_case(request: Request) -> GetCurationUseCase:
    return GetCurationService(
        uow=new_unit_of_work(request),
        status_policy=request.app.state.exhibit_status_policy,
    )


def build_pick_curation_use_case(request: Request) -> PickCurationUseCase:
    return PickCurationService(
        uow=new_unit_of_work(request),
        status_policy=request.app.state.exhibit_status_policy,
        size=settings.home_screen.curation_size,
    )


def build_search_curations_use_case(request: Request) -> SearchCurationsUseCase:
    return SearchCurationsService(uow=new_unit_of_work(request))


def build_get_managed_curation_use_case(request: Request) -> GetManagedCurationUseCase:
    return GetManagedCurationService(
        uow=new_unit_of_work(request),
        status_policy=request.app.state.exhibit_status_policy,
    )


def build_create_curation_use_case(request: Request) -> CreateCurationUseCase:
    return CreateCurationService(uow=new_unit_of_work(request))


def build_update_curation_use_case(request: Request) -> UpdateCurationUseCase:
    return UpdateCurationService(uow=new_unit_of_work(request))


def build_delete_curation_use_case(request: Request) -> DeleteCurationUseCase:
    return DeleteCurationService(uow=new_unit_of_work(request))


def wire_curation(overrides: Overrides) -> None:
    overrides[provide_get_curation_use_case] = build_get_curation_use_case
    overrides[provide_pick_curation_use_case] = build_pick_curation_use_case
    overrides[provide_search_curations_use_case] = build_search_curations_use_case
    overrides[provide_get_managed_curation_use_case] = (
        build_get_managed_curation_use_case
    )
    overrides[provide_create_curation_use_case] = build_create_curation_use_case
    overrides[provide_update_curation_use_case] = build_update_curation_use_case
    overrides[provide_delete_curation_use_case] = build_delete_curation_use_case
