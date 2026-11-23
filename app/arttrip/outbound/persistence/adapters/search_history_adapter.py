from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from arttrip.application.domain.search_history.search_history import SearchHistory
from arttrip.application.port.output.search_history_port import SearchHistoryPort
from arttrip.outbound.persistence.models import search_history_table


class SearchHistoryAdapter(SearchHistoryPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, history: SearchHistory) -> None:
        self._session.execute(
            delete(search_history_table).where(
                search_history_table.c.user_id == history.user_id,
                search_history_table.c.content == history.content,
            )
        )
        self._session.execute(
            insert(search_history_table)
            .values(
                user_id=history.user_id,
                content=history.content,
                created_at=history.created_at,
            )
            .on_conflict_do_nothing(
                index_elements=[
                    search_history_table.c.user_id,
                    search_history_table.c.content,
                ]
            )
        )

    def keep_latest(self, *, user_id: int, count: int) -> None:
        latest_ids = (
            select(search_history_table.c.id)
            .where(search_history_table.c.user_id == user_id)
            .order_by(
                search_history_table.c.created_at.desc(),
                search_history_table.c.id.desc(),
            )
            .limit(count)
        )
        self._session.execute(
            delete(search_history_table).where(
                search_history_table.c.user_id == user_id,
                search_history_table.c.id.not_in(latest_ids),
            )
        )

    def list_recent(self, *, user_id: int, limit: int) -> list[SearchHistory]:
        statement = (
            select(SearchHistory)
            .where(search_history_table.c.user_id == user_id)
            .order_by(
                search_history_table.c.created_at.desc(),
                search_history_table.c.id.desc(),
            )
            .limit(limit)
        )
        return list(self._session.scalars(statement).all())

    def remove(self, *, user_id: int, history_id: int) -> int | None:
        statement = (
            delete(search_history_table)
            .where(
                search_history_table.c.id == history_id,
                search_history_table.c.user_id == user_id,
            )
            .returning(search_history_table.c.id)
        )
        return self._session.execute(statement).scalar_one_or_none()

    def remove_all(self, user_id: int) -> None:
        self._session.execute(
            delete(search_history_table).where(
                search_history_table.c.user_id == user_id
            )
        )
