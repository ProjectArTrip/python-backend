from typing import Annotated

from fastapi import APIRouter, Path, status

from arttrip.application.domain.search_history.exceptions import SearchHistoryError
from arttrip.application.port.input.search_history.commands import (
    AddSearchHistoryCommand,
    RemoveSearchHistoryCommand,
)
from arttrip.inbound.http.dependencies.auth import CurrentUserDep
from arttrip.inbound.http.dependencies.search_history import (
    AddSearchHistoryUseCaseDep,
    ClearSearchHistoryUseCaseDep,
    ListSearchHistoryUseCaseDep,
    RemoveSearchHistoryUseCaseDep,
)
from arttrip.inbound.http.openapi import AUTHENTICATION_ERRORS, error_responses
from arttrip.inbound.http.schemas.search_history import (
    AddSearchHistoryRequest,
    SearchHistoryListResponse,
    SearchHistoryResponse,
)

router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=error_responses(
        *AUTHENTICATION_ERRORS,
        SearchHistoryError.blank_keyword,
        SearchHistoryError.keyword_too_long,
    ),
)
def add_search_history(
    body: AddSearchHistoryRequest,
    current_user: CurrentUserDep,
    use_case: AddSearchHistoryUseCaseDep,
) -> None:
    use_case.add_search_history(
        AddSearchHistoryCommand(user_id=current_user.user_id, keyword=body.keyword)
    )


@router.get(
    "",
    response_model=SearchHistoryListResponse,
    responses=error_responses(*AUTHENTICATION_ERRORS),
)
def list_search_history(
    current_user: CurrentUserDep,
    use_case: ListSearchHistoryUseCaseDep,
) -> SearchHistoryListResponse:
    items = use_case.list_search_history(current_user.user_id)
    return SearchHistoryListResponse(
        items=[
            SearchHistoryResponse(
                search_history_id=item.search_history_id,
                keyword=item.keyword,
                searched_at=item.searched_at,
            )
            for item in items
        ]
    )


@router.delete(
    "/{search_history_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=error_responses(*AUTHENTICATION_ERRORS, SearchHistoryError.not_found),
)
def remove_search_history(
    search_history_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUserDep,
    use_case: RemoveSearchHistoryUseCaseDep,
) -> None:
    use_case.remove_search_history(
        RemoveSearchHistoryCommand(
            user_id=current_user.user_id, search_history_id=search_history_id
        )
    )


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=error_responses(*AUTHENTICATION_ERRORS),
)
def clear_search_history(
    current_user: CurrentUserDep,
    use_case: ClearSearchHistoryUseCaseDep,
) -> None:
    use_case.clear_search_history(current_user.user_id)
