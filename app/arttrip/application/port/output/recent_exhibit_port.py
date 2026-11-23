from abc import ABC, abstractmethod
from datetime import datetime

from arttrip.application.domain.exhibit.exhibit import Exhibit


class RecentExhibitPort(ABC):
    @abstractmethod
    def record(self, *, user_id: int, exhibit_id: int, viewed_at: datetime) -> None:
        pass

    @abstractmethod
    def list_exhibits(
        self, *, user_id: int, since: datetime, limit: int
    ) -> list[Exhibit]:
        pass
