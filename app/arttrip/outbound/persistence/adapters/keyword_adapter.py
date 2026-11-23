from typing import Collection

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from arttrip.application.domain.keyword.keyword import Keyword
from arttrip.application.domain.keyword.keyword_type import KeywordType
from arttrip.application.port.output.keyword_port import KeywordPort
from arttrip.outbound.persistence.models import keyword_table, user_keyword_table


class KeywordAdapter(KeywordPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[Keyword]:
        statement = select(Keyword).order_by(keyword_table.c.type, keyword_table.c.id)
        return list(self._session.scalars(statement).all())

    def find_by_ids(self, keyword_ids: Collection[int]) -> list[Keyword]:
        statement = select(Keyword).where(keyword_table.c.id.in_(keyword_ids))
        return list(self._session.scalars(statement).all())

    def find_by_names(
        self, *, keyword_type: KeywordType, names: Collection[str]
    ) -> list[Keyword]:
        wanted = {Keyword.normalize_name(name) for name in names}
        statement = select(Keyword).where(
            keyword_table.c.type == keyword_type,
            keyword_table.c.name.in_(wanted),
        )
        return list(self._session.scalars(statement).all())

    def list_random_selected(self, *, user_id: int, limit: int) -> list[Keyword]:
        statement = (
            select(Keyword)
            .join(
                user_keyword_table,
                user_keyword_table.c.keyword_id == keyword_table.c.id,
            )
            .where(user_keyword_table.c.user_id == user_id)
            .order_by(func.random())
            .limit(limit)
        )
        return list(self._session.scalars(statement).all())

    def find_interested_user_ids(self, keyword_ids: Collection[int]) -> set[int]:
        if not keyword_ids:
            return set()
        statement = (
            select(user_keyword_table.c.user_id)
            .where(user_keyword_table.c.keyword_id.in_(keyword_ids))
            .distinct()
        )
        return set(self._session.scalars(statement))
