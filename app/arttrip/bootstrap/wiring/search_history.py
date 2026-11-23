from fastapi import Request

from arttrip.application.domain.search_history.search_history_services import (
    AddSearchHistoryService,
    ClearSearchHistoryService,
    ListSearchHistoryService,
    RemoveSearchHistoryService,
)
from arttrip.application.port.input.search_history.use_cases import (
    AddSearchHistoryUseCase,
    ClearSearchHistoryUseCase,
    ListSearchHistoryUseCase,
    RemoveSearchHistoryUseCase,
)
from arttrip.bootstrap.wiring.common import Overrides, new_unit_of_work
from arttrip.inbound.http.dependencies.search_history import (
    provide_add_search_history_use_case,
    provide_clear_search_history_use_case,
    provide_list_search_history_use_case,
    provide_remove_search_history_use_case,
)


def build_add_search_history_use_case(request: Request) -> AddSearchHistoryUseCase:
    return AddSearchHistoryService(
        uow=new_unit_of_work(request), policy=request.app.state.search_history_policy
    )


def build_list_search_history_use_case(request: Request) -> ListSearchHistoryUseCase:
    return ListSearchHistoryService(
        uow=new_unit_of_work(request), policy=request.app.state.search_history_policy
    )


def build_remove_search_history_use_case(
    request: Request,
) -> RemoveSearchHistoryUseCase:
    return RemoveSearchHistoryService(uow=new_unit_of_work(request))


def build_clear_search_history_use_case(
    request: Request,
) -> ClearSearchHistoryUseCase:
    return ClearSearchHistoryService(uow=new_unit_of_work(request))


def wire_search_history(overrides: Overrides) -> None:
    overrides[provide_add_search_history_use_case] = build_add_search_history_use_case
    overrides[provide_list_search_history_use_case] = build_list_search_history_use_case
    overrides[provide_remove_search_history_use_case] = (
        build_remove_search_history_use_case
    )
    overrides[provide_clear_search_history_use_case] = (
        build_clear_search_history_use_case
    )
