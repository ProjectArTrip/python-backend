from datetime import UTC, datetime

from arttrip.application.domain.exhibit.exceptions import ExhibitError
from arttrip.application.domain.exhibit.exhibit_services import to_exhibit_summary
from arttrip.application.domain.exhibit.exhibit_status_policy import ExhibitStatusPolicy
from arttrip.application.domain.favorite.favorite import Favorite
from arttrip.application.domain.user.current_user import load_current_user
from arttrip.application.port.input.favorite.commands import (
    AddFavoriteCommand,
    RemoveFavoriteCommand,
)
from arttrip.application.port.input.favorite.queries import ListFavoritesQuery
from arttrip.application.port.input.favorite.results import ListFavoritesResult
from arttrip.application.port.input.favorite.use_cases import (
    AddFavoriteUseCase,
    ListFavoritesUseCase,
    RemoveFavoriteUseCase,
)
from arttrip.application.port.input.pagination import CursorPage
from arttrip.application.port.output.unit_of_work import UnitOfWork
from arttrip.application.util.service_date import to_service_date


class AddFavoriteService(AddFavoriteUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def add_favorite(self, command: AddFavoriteCommand) -> None:
        with self._uow as uow:
            load_current_user(uow.users, command.user_id)
            if uow.exhibits.find_by_id(command.exhibit_id) is None:
                raise ExhibitError.not_found()
            uow.favorites.add(
                Favorite.create(
                    user_id=command.user_id,
                    exhibit_id=command.exhibit_id,
                    now=datetime.now(UTC),
                )
            )


class RemoveFavoriteService(RemoveFavoriteUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def remove_favorite(self, command: RemoveFavoriteCommand) -> None:
        with self._uow as uow:
            uow.favorites.remove(user_id=command.user_id, exhibit_id=command.exhibit_id)


class ListFavoritesService(ListFavoritesUseCase):
    def __init__(self, *, uow: UnitOfWork, status_policy: ExhibitStatusPolicy) -> None:
        self._uow = uow
        self._status_policy = status_policy

    def list_favorites(self, query: ListFavoritesQuery) -> ListFavoritesResult:
        today = to_service_date(datetime.now(UTC))
        with self._uow as uow:
            rows = uow.favorites.list_page(
                user_id=query.user_id,
                criteria=query.criteria,
                sort=query.sort,
                today=today,
                cursor=query.cursor,
                limit=query.size + 1,
            )
            has_next = len(rows) > query.size
            page_rows = rows[: query.size]
            next_cursor = page_rows[-1].cursor if has_next else None
            total_count = uow.favorites.count(
                user_id=query.user_id, criteria=query.criteria
            )
            return ListFavoritesResult(
                page=CursorPage(
                    items=tuple(
                        to_exhibit_summary(
                            row.exhibit,
                            status=row.exhibit.status_on(
                                today=today, policy=self._status_policy
                            ),
                            is_favorite=True,
                        )
                        for row in page_rows
                    ),
                    next_cursor=next_cursor,
                ),
                total_count=total_count,
            )
