from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class UpdateExhibitCommand:
    exhibit_id: int
    title: str
    description: str | None
    poster_url: str | None
    ticket_url: str | None
    start_date: date | None
    end_date: date | None
    hall_name: str
    country_name: str
    region: str
    address: str | None
    opening_hours: str | None
    phone: str | None
    latitude: Decimal | None
    longitude: Decimal | None
    genre_names: frozenset[str]
    style_names: frozenset[str]
    is_domestic: bool | None


@dataclass(frozen=True)
class CreateExhibitCommand:
    title: str
    description: str | None
    poster_url: str | None
    ticket_url: str | None
    start_date: date | None
    end_date: date | None
    hall_name: str
    country_name: str
    region: str
    address: str | None
    opening_hours: str | None
    phone: str | None
    latitude: Decimal
    longitude: Decimal
    genre_names: frozenset[str]
    style_names: frozenset[str]
    is_domestic: bool | None


@dataclass(frozen=True)
class ExhibitImportRow:
    row_number: int
    exhibit: CreateExhibitCommand


@dataclass(frozen=True)
class RegisterArtistExhibitCommand:
    artist_id: int
    exhibit: CreateExhibitCommand


@dataclass(frozen=True)
class UpdateArtistExhibitCommand:
    artist_id: int
    exhibit_id: int
    exhibit: CreateExhibitCommand


@dataclass(frozen=True)
class DeleteArtistExhibitCommand:
    artist_id: int
    exhibit_id: int
