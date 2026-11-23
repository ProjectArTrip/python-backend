from sqlalchemy import select
from sqlalchemy.orm import Session

from arttrip.application.port.output.banned_word_port import BannedWordPort
from arttrip.outbound.persistence.models import banned_word_table


class BannedWordAdapter(BannedWordPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_active_words(self) -> list[str]:
        statement = select(banned_word_table.c.word).where(
            banned_word_table.c.active.is_(True)
        )
        return list(self._session.scalars(statement))
