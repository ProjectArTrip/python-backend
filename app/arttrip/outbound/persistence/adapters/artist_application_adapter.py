from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from arttrip.application.domain.artist_application.artist_application import (
    ArtistApplication,
)
from arttrip.application.domain.artist_application.artist_application_status import (
    ArtistApplicationStatus,
)
from arttrip.application.domain.artist_application.exceptions import (
    ArtistApplicationError,
)
from arttrip.application.port.output.artist_application_port import (
    ArtistApplicationPort,
)
from arttrip.outbound.persistence.models import artist_application_table


class ArtistApplicationAdapter(ArtistApplicationPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, application: ArtistApplication) -> None:
        self._session.add(application)
        try:
            self._session.flush()
        except IntegrityError as error:
            raise ArtistApplicationError.already_pending() from error

    def find_pending_by_user_id(self, user_id: int) -> ArtistApplication | None:
        statement = select(ArtistApplication).where(
            artist_application_table.c.user_id == user_id,
            artist_application_table.c.status == ArtistApplicationStatus.PENDING,
        )
        return self._session.scalars(statement).one_or_none()

    def find_latest_by_user_id(self, user_id: int) -> ArtistApplication | None:
        statement = (
            select(ArtistApplication)
            .where(artist_application_table.c.user_id == user_id)
            .order_by(artist_application_table.c.id.desc())
            .limit(1)
        )
        return self._session.scalars(statement).one_or_none()

    def find_by_id(self, application_id: int) -> ArtistApplication | None:
        return self._session.get(ArtistApplication, application_id)

    def list_page(
        self,
        *,
        status: ArtistApplicationStatus | None,
        cursor: int | None,
        limit: int,
    ) -> list[ArtistApplication]:
        statement = (
            select(ArtistApplication)
            .order_by(artist_application_table.c.id.desc())
            .limit(limit)
        )
        if status is not None:
            statement = statement.where(artist_application_table.c.status == status)
        if cursor is not None:
            statement = statement.where(artist_application_table.c.id < cursor)
        return list(self._session.scalars(statement).all())
