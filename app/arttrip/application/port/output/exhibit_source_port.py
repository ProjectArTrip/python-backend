import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class SourcedExhibit:
    source: str
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

    def content_hash(self) -> str:
        payload = json.dumps(asdict(self), ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SourcedExhibitPage:
    items: tuple[SourcedExhibit, ...]
    total_count: int


class ExhibitSourcePort(ABC):
    @abstractmethod
    def fetch_page(self, *, page_no: int, size: int) -> SourcedExhibitPage:
        pass
