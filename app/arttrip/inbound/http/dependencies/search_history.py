from typing import Annotated

from fastapi import Depends

from arttrip.application.port.input.search_history.use_cases import (
    AddSearchHistoryUseCase,
    ClearSearchHistoryUseCase,
    ListSearchHistoryUseCase,
    RemoveSearchHistoryUseCase,
)


def provide_add_search_history_use_case() -> AddSearchHistoryUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_list_search_history_use_case() -> ListSearchHistoryUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_remove_search_history_use_case() -> RemoveSearchHistoryUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_clear_search_history_use_case() -> ClearSearchHistoryUseCase:
    raise NotImplementedError("composition root must override this dependency")


AddSearchHistoryUseCaseDep = Annotated[
    AddSearchHistoryUseCase, Depends(provide_add_search_history_use_case)
]
ListSearchHistoryUseCaseDep = Annotated[
    ListSearchHistoryUseCase, Depends(provide_list_search_history_use_case)
]
RemoveSearchHistoryUseCaseDep = Annotated[
    RemoveSearchHistoryUseCase, Depends(provide_remove_search_history_use_case)
]
ClearSearchHistoryUseCaseDep = Annotated[
    ClearSearchHistoryUseCase, Depends(provide_clear_search_history_use_case)
]
