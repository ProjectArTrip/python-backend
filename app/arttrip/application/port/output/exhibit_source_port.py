from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class SourcedExhibit:
    external_id: str
    title: str | None
    description: str | None
    poster_url: str | None
    ticket_url: str | None
    start_date: str | None
    end_date: str | None
    place_name: str | None
    country: str | None
    region: str | None
    address: str | None
    phone: str | None
    latitude: str | None
    longitude: str | None


@dataclass(frozen=True)
class SourcedExhibitPage:
    items: tuple[SourcedExhibit, ...]
    total_count: int


class ExhibitSourcePort(ABC):
    @abstractmethod
    def fetch_page(self, *, page_no: int, size: int) -> SourcedExhibitPage:
        pass
