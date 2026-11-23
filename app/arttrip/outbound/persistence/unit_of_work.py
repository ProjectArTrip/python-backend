from types import TracebackType
from typing import Self

from sqlalchemy.orm import Session, sessionmaker

from arttrip.application.port.output.unit_of_work import UnitOfWork
from arttrip.outbound.persistence.adapters.artist_application_adapter import (
    ArtistApplicationAdapter,
)
from arttrip.outbound.persistence.adapters.banned_word_adapter import BannedWordAdapter
from arttrip.outbound.persistence.adapters.curation_adapter import CurationAdapter
from arttrip.outbound.persistence.adapters.device_token_adapter import (
    DeviceTokenAdapter,
)
from arttrip.outbound.persistence.adapters.exhibit_adapter import ExhibitAdapter
from arttrip.outbound.persistence.adapters.favorite_adapter import FavoriteAdapter
from arttrip.outbound.persistence.adapters.keyword_adapter import KeywordAdapter
from arttrip.outbound.persistence.adapters.location_adapter import LocationAdapter
from arttrip.outbound.persistence.adapters.notification_adapter import (
    NotificationAdapter,
)
from arttrip.outbound.persistence.adapters.push_dispatch_adapter import (
    PushDispatchAdapter,
)
from arttrip.outbound.persistence.adapters.recent_exhibit_adapter import (
    RecentExhibitAdapter,
)
from arttrip.outbound.persistence.adapters.review_adapter import ReviewAdapter
from arttrip.outbound.persistence.adapters.search_history_adapter import (
    SearchHistoryAdapter,
)
from arttrip.outbound.persistence.adapters.user_adapter import UserAdapter
from arttrip.outbound.persistence.integrity import translate_integrity_errors


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def __enter__(self) -> Self:
        self._session = self._session_factory()
        self.users = UserAdapter(self._session)
        self.keywords = KeywordAdapter(self._session)
        self.locations = LocationAdapter(self._session)
        self.device_tokens = DeviceTokenAdapter(self._session)
        self.exhibits = ExhibitAdapter(self._session)
        self.artist_applications = ArtistApplicationAdapter(self._session)
        self.notifications = NotificationAdapter(self._session)
        self.favorites = FavoriteAdapter(self._session)
        self.recent_exhibits = RecentExhibitAdapter(self._session)
        self.curations = CurationAdapter(self._session)
        self.search_histories = SearchHistoryAdapter(self._session)
        self.push_dispatches = PushDispatchAdapter(self._session)
        self.reviews = ReviewAdapter(self._session)
        self.banned_words = BannedWordAdapter(self._session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        try:
            if exc_type is None:
                with translate_integrity_errors():
                    self._session.commit()
            else:
                self._session.rollback()
        finally:
            self._session.close()
