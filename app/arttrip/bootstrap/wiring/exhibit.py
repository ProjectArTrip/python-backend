from fastapi import Request

from arttrip.application.domain.exhibit.artist_exhibit_services import (
    DeleteArtistExhibitService,
    ListArtistExhibitsService,
    RegisterArtistExhibitService,
    UpdateArtistExhibitService,
)
from arttrip.application.domain.exhibit.exhibit_import_services import (
    FetchOpenDataExhibitsService,
    GetExhibitImportGuideService,
    ImportExhibitsService,
    PreviewExhibitImportService,
)
from arttrip.application.domain.exhibit.exhibit_management_services import (
    CreateExhibitService,
    DeleteExhibitService,
    GetManagedExhibitService,
    SearchExhibitsService,
    UpdateExhibitService,
)
from arttrip.application.domain.exhibit.exhibit_services import (
    GetExhibitService,
    ListExhibitsService,
    ListRecentExhibitsService,
)
from arttrip.application.port.input.exhibit.use_cases import (
    CreateExhibitUseCase,
    DeleteArtistExhibitUseCase,
    DeleteExhibitUseCase,
    FetchOpenDataExhibitsUseCase,
    GetExhibitImportGuideUseCase,
    GetExhibitUseCase,
    GetManagedExhibitUseCase,
    ImportExhibitsUseCase,
    ListArtistExhibitsUseCase,
    ListExhibitsUseCase,
    ListRecentExhibitsUseCase,
    PreviewExhibitImportUseCase,
    RegisterArtistExhibitUseCase,
    SearchExhibitsUseCase,
    UpdateArtistExhibitUseCase,
    UpdateExhibitUseCase,
)
from arttrip.bootstrap.wiring.common import Overrides, new_unit_of_work
from arttrip.bootstrap.wiring.notification import build_send_push_use_case
from arttrip.common import settings
from arttrip.inbound.http.dependencies.exhibit import (
    provide_create_exhibit_use_case,
    provide_delete_artist_exhibit_use_case,
    provide_delete_exhibit_use_case,
    provide_fetch_open_data_exhibits_use_case,
    provide_get_exhibit_import_guide_use_case,
    provide_get_exhibit_use_case,
    provide_get_managed_exhibit_use_case,
    provide_import_exhibits_use_case,
    provide_list_artist_exhibits_use_case,
    provide_list_exhibits_use_case,
    provide_list_recent_exhibits_use_case,
    provide_preview_exhibit_import_use_case,
    provide_register_artist_exhibit_use_case,
    provide_search_exhibits_use_case,
    provide_update_artist_exhibit_use_case,
    provide_update_exhibit_use_case,
)


def build_get_exhibit_use_case(request: Request) -> GetExhibitUseCase:
    return GetExhibitService(
        uow=new_unit_of_work(request),
        status_policy=request.app.state.exhibit_status_policy,
    )


def build_list_exhibits_use_case(request: Request) -> ListExhibitsUseCase:
    return ListExhibitsService(
        uow=new_unit_of_work(request),
        status_policy=request.app.state.exhibit_status_policy,
    )


def build_list_recent_exhibits_use_case(request: Request) -> ListRecentExhibitsUseCase:
    return ListRecentExhibitsService(
        uow=new_unit_of_work(request),
        status_policy=request.app.state.exhibit_status_policy,
        size=settings.exhibit.recent_list_size,
        retention_days=settings.exhibit.recent_retention_days,
    )


def build_search_exhibits_use_case(request: Request) -> SearchExhibitsUseCase:
    return SearchExhibitsService(
        uow=new_unit_of_work(request),
        status_policy=request.app.state.exhibit_status_policy,
    )


def build_get_managed_exhibit_use_case(request: Request) -> GetManagedExhibitUseCase:
    return GetManagedExhibitService(
        uow=new_unit_of_work(request),
        status_policy=request.app.state.exhibit_status_policy,
    )


def build_update_exhibit_use_case(request: Request) -> UpdateExhibitUseCase:
    return UpdateExhibitService(uow=new_unit_of_work(request))


def build_delete_exhibit_use_case(request: Request) -> DeleteExhibitUseCase:
    return DeleteExhibitService(uow=new_unit_of_work(request))


def build_create_exhibit_use_case(request: Request) -> CreateExhibitUseCase:
    return CreateExhibitService(
        uow=new_unit_of_work(request),
        status_policy=request.app.state.exhibit_status_policy,
        send_push=build_send_push_use_case(request),
    )


def build_preview_exhibit_import_use_case(
    request: Request,
) -> PreviewExhibitImportUseCase:
    return PreviewExhibitImportService(
        uow=new_unit_of_work(request),
        status_policy=request.app.state.exhibit_status_policy,
    )


def build_get_exhibit_import_guide_use_case(
    request: Request,
) -> GetExhibitImportGuideUseCase:
    return GetExhibitImportGuideService(uow=new_unit_of_work(request))


def build_import_exhibits_use_case(request: Request) -> ImportExhibitsUseCase:
    return ImportExhibitsService(
        uow=new_unit_of_work(request),
        status_policy=request.app.state.exhibit_status_policy,
    )


def build_register_artist_exhibit_use_case(
    request: Request,
) -> RegisterArtistExhibitUseCase:
    return RegisterArtistExhibitService(
        uow=new_unit_of_work(request),
        status_policy=request.app.state.exhibit_status_policy,
    )


def build_list_artist_exhibits_use_case(request: Request) -> ListArtistExhibitsUseCase:
    return ListArtistExhibitsService(
        uow=new_unit_of_work(request),
        status_policy=request.app.state.exhibit_status_policy,
    )


def build_update_artist_exhibit_use_case(
    request: Request,
) -> UpdateArtistExhibitUseCase:
    return UpdateArtistExhibitService(uow=new_unit_of_work(request))


def build_delete_artist_exhibit_use_case(
    request: Request,
) -> DeleteArtistExhibitUseCase:
    return DeleteArtistExhibitService(uow=new_unit_of_work(request))


def build_fetch_open_data_exhibits_use_case(
    request: Request,
) -> FetchOpenDataExhibitsUseCase:
    return FetchOpenDataExhibitsService(
        source=request.app.state.exhibit_source,
        page_size=settings.opendata.page_size,
    )


def wire_exhibit(overrides: Overrides) -> None:
    overrides[provide_get_exhibit_use_case] = build_get_exhibit_use_case
    overrides[provide_list_exhibits_use_case] = build_list_exhibits_use_case
    overrides[provide_list_recent_exhibits_use_case] = (
        build_list_recent_exhibits_use_case
    )
    overrides[provide_search_exhibits_use_case] = build_search_exhibits_use_case
    overrides[provide_get_managed_exhibit_use_case] = build_get_managed_exhibit_use_case
    overrides[provide_update_exhibit_use_case] = build_update_exhibit_use_case
    overrides[provide_delete_exhibit_use_case] = build_delete_exhibit_use_case
    overrides[provide_create_exhibit_use_case] = build_create_exhibit_use_case
    overrides[provide_get_exhibit_import_guide_use_case] = (
        build_get_exhibit_import_guide_use_case
    )
    overrides[provide_preview_exhibit_import_use_case] = (
        build_preview_exhibit_import_use_case
    )
    overrides[provide_import_exhibits_use_case] = build_import_exhibits_use_case
    overrides[provide_register_artist_exhibit_use_case] = (
        build_register_artist_exhibit_use_case
    )
    overrides[provide_list_artist_exhibits_use_case] = (
        build_list_artist_exhibits_use_case
    )
    overrides[provide_update_artist_exhibit_use_case] = (
        build_update_artist_exhibit_use_case
    )
    overrides[provide_delete_artist_exhibit_use_case] = (
        build_delete_artist_exhibit_use_case
    )
    overrides[provide_fetch_open_data_exhibits_use_case] = (
        build_fetch_open_data_exhibits_use_case
    )
