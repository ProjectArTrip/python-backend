from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from arttrip.application.domain.exhibit.exhibit import Exhibit
from arttrip.application.port.output.recent_exhibit_port import RecentExhibitPort
from arttrip.outbound.persistence.models import exhibit_table, recent_exhibit_table


class RecentExhibitAdapter(RecentExhibitPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def record(self, *, user_id: int, exhibit_id: int, viewed_at: datetime) -> None:
        statement = insert(recent_exhibit_table).values(
            user_id=user_id, exhibit_id=exhibit_id, viewed_at=viewed_at
        )
        statement = statement.on_conflict_do_update(
            index_elements=[
                recent_exhibit_table.c.user_id,
                recent_exhibit_table.c.exhibit_id,
            ],
            set_={"viewed_at": statement.excluded.viewed_at},
        )
        self._session.execute(statement)

    def list_exhibits(
        self, *, user_id: int, since: datetime, limit: int
    ) -> list[Exhibit]:
        statement = (
            select(Exhibit)
            .join(
                recent_exhibit_table,
                recent_exhibit_table.c.exhibit_id == exhibit_table.c.id,
            )
            .where(
                recent_exhibit_table.c.user_id == user_id,
                recent_exhibit_table.c.viewed_at >= since,
            )
            .order_by(
                recent_exhibit_table.c.viewed_at.desc(),
                recent_exhibit_table.c.id.desc(),
            )
            .limit(limit)
        )
        return list(self._session.scalars(statement).all())
