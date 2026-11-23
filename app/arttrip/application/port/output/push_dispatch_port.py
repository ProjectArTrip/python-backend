from abc import ABC, abstractmethod

from arttrip.application.domain.notification.push_dispatch import PushDispatch


class PushDispatchPort(ABC):
    @abstractmethod
    def add(self, dispatch: PushDispatch) -> None:
        pass

    @abstractmethod
    def find_by_id(self, dispatch_id: int) -> PushDispatch | None:
        pass
