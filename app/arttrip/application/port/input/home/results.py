from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class HomeVenue:
    venue_id: int
    name: str
    region: str
    latitude: Decimal
    longitude: Decimal
    ongoing_exhibit_count: int
