from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from arttrip.application.port.output.artist_application_port import (
    ArtistApplicationPort,
)
from arttrip.application.port.output.banned_word_port import BannedWordPort
from arttrip.application.port.output.curation_port import CurationPort
from arttrip.application.port.output.device_token_port import DeviceTokenPort
from arttrip.application.port.output.exhibit_port import ExhibitPort
from arttrip.application.port.output.favorite_port import FavoritePort
from arttrip.application.port.output.keyword_port import KeywordPort
from arttrip.application.port.output.location_port import LocationPort
from arttrip.application.port.output.notification_port import NotificationPort
from arttrip.application.port.output.push_dispatch_port import PushDispatchPort
from arttrip.application.port.output.recent_exhibit_port import RecentExhibitPort
from arttrip.application.port.output.review_port import ReviewPort
from arttrip.application.port.output.search_history_port import SearchHistoryPort
from arttrip.application.port.output.user_port import UserPort


class UnitOfWork(ABC):
    users: UserPort
    keywords: KeywordPort
    locations: LocationPort
    device_tokens: DeviceTokenPort
    exhibits: ExhibitPort
    artist_applications: ArtistApplicationPort
    notifications: NotificationPort
    favorites: FavoritePort
    recent_exhibits: RecentExhibitPort
    curations: CurationPort
    search_histories: SearchHistoryPort
    push_dispatches: PushDispatchPort
    reviews: ReviewPort
    banned_words: BannedWordPort

    @abstractmethod
    def __enter__(self) -> Self:
        pass

    @abstractmethod
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        pass
