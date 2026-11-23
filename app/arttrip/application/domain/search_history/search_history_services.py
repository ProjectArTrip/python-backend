from datetime import UTC, datetime

from arttrip.application.domain.search_history.exceptions import SearchHistoryError
from arttrip.application.domain.search_history.search_history import SearchHistory
from arttrip.application.domain.search_history.search_history_policy import (
    SearchHistoryPolicy,
)
from arttrip.application.domain.user.current_user import load_current_user
from arttrip.application.port.input.search_history.commands import (
    AddSearchHistoryCommand,
    RemoveSearchHistoryCommand,
)
from arttrip.application.port.input.search_history.results import SearchHistoryItem
from arttrip.application.port.input.search_history.use_cases import (
    AddSearchHistoryUseCase,
    ClearSearchHistoryUseCase,
    ListSearchHistoryUseCase,
    RemoveSearchHistoryUseCase,
)
from arttrip.application.port.output.unit_of_work import UnitOfWork


class AddSearchHistoryService(AddSearchHistoryUseCase):
    def __init__(self, *, uow: UnitOfWork, policy: SearchHistoryPolicy) -> None:
        self._uow = uow
        self._policy = policy

    def add_search_history(self, command: AddSearchHistoryCommand) -> None:
        history = SearchHistory.create(
            user_id=command.user_id,
            keyword=command.keyword,
            policy=self._policy,
            now=datetime.now(UTC),
        )
        with self._uow as uow:
            load_current_user(uow.users, command.user_id)
            uow.search_histories.add(history)
            uow.search_histories.keep_latest(
                user_id=command.user_id, count=self._policy.max_count
            )


class ListSearchHistoryService(ListSearchHistoryUseCase):
    def __init__(self, *, uow: UnitOfWork, policy: SearchHistoryPolicy) -> None:
        self._uow = uow
        self._policy = policy

    def list_search_history(self, user_id: int) -> tuple[SearchHistoryItem, ...]:
        with self._uow as uow:
            histories = uow.search_histories.list_recent(
                user_id=user_id, limit=self._policy.max_count
            )
            return tuple(
                SearchHistoryItem(
                    search_history_id=history.id,
                    keyword=history.content,
                    searched_at=history.created_at,
                )
                for history in histories
                if history.id is not None
            )


class RemoveSearchHistoryService(RemoveSearchHistoryUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def remove_search_history(self, command: RemoveSearchHistoryCommand) -> None:
        with self._uow as uow:
            removed_id = uow.search_histories.remove(
                user_id=command.user_id, history_id=command.search_history_id
            )
            if removed_id is None:
                raise SearchHistoryError.not_found()


class ClearSearchHistoryService(ClearSearchHistoryUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def clear_search_history(self, user_id: int) -> None:
        with self._uow as uow:
            uow.search_histories.remove_all(user_id)
