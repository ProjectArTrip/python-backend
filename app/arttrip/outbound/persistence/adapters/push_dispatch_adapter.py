from sqlalchemy.orm import Session

from arttrip.application.domain.notification.push_dispatch import PushDispatch
from arttrip.application.port.output.push_dispatch_port import PushDispatchPort


class PushDispatchAdapter(PushDispatchPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, dispatch: PushDispatch) -> None:
        self._session.add(dispatch)
        self._session.flush()

    def find_by_id(self, dispatch_id: int) -> PushDispatch | None:
        return self._session.get(PushDispatch, dispatch_id)
