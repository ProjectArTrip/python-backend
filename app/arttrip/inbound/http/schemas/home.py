from pydantic import Field

from arttrip.inbound.http.schemas.base import ApiModel
from arttrip.inbound.http.schemas.exhibits import ExhibitSummaryResponse


class HomeExhibitListResponse(ApiModel):
    exhibits: list[ExhibitSummaryResponse]


class HomeGenreParams(ApiModel):
    genre_id: int = Field(gt=0)


class HomeVenueResponse(ApiModel):
    venue_id: int
    name: str
    region: str
    latitude: float
    longitude: float
    ongoing_exhibit_count: int


class HomeVenueListResponse(ApiModel):
    venues: list[HomeVenueResponse]
