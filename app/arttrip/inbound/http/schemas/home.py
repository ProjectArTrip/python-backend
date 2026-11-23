from datetime import date

from pydantic import Field

from arttrip.inbound.http.query_params import CountryCode, Region
from arttrip.inbound.http.schemas.base import ApiModel
from arttrip.inbound.http.schemas.exhibits import ExhibitSummaryResponse


class HomeExhibitListResponse(ApiModel):
    exhibits: list[ExhibitSummaryResponse]


class HomeLocationParams(ApiModel):
    domestic: bool
    country_code: CountryCode = None
    region: Region = None


class HomeScheduleParams(HomeLocationParams):
    scheduled_date: date


class HomeGenreParams(ApiModel):
    genre_id: int = Field(gt=0)
