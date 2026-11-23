from datetime import date
from typing import Final

from pydantic import Field

from arttrip.application.domain.exhibit.exhibit_list_sort import ExhibitListSort
from arttrip.application.domain.exhibit.exhibit_status import ExhibitStatus
from arttrip.inbound.http.pagination import DEFAULT_PAGE_SIZE, PageSize
from arttrip.inbound.http.query_params import CountryCode, SearchText
from arttrip.inbound.http.schemas.base import ApiModel

MAX_FILTER_VALUE: Final = 20
CURSOR_MAX_LENGTH: Final = 200


class ExhibitHallResponse(ApiModel):
    name: str
    address: str | None
    phone: str | None
    homepage_url: str | None
    opening_hours: str | None
    closed_days: str | None
    region: str
    country_code: str
    latitude: float
    longitude: float


class ExhibitHallSummaryResponse(ApiModel):
    name: str
    region: str
    country_code: str


class ExhibitDetailResponse(ApiModel):
    exhibit_id: int
    title: str | None
    description: str | None
    poster_url: str | None
    ticket_url: str | None
    status: ExhibitStatus
    start_date: date | None
    end_date: date | None
    hall: ExhibitHallResponse
    is_favorite: bool
    review_count: int


class ExhibitSummaryResponse(ApiModel):
    exhibit_id: int
    title: str | None
    poster_url: str | None
    status: ExhibitStatus
    start_date: date | None
    end_date: date | None
    hall: ExhibitHallSummaryResponse
    is_favorite: bool


class ExhibitListResponse(ApiModel):
    exhibits: list[ExhibitSummaryResponse]
    next_cursor: str | None
    has_next: bool


class RecentExhibitListResponse(ApiModel):
    exhibits: list[ExhibitSummaryResponse]


class CountryResponse(ApiModel):
    country_code: str
    name: str


class CountryListResponse(ApiModel):
    countries: list[CountryResponse]


class RegionResponse(ApiModel):
    region: str
    image_url: str | None


class RegionListResponse(ApiModel):
    regions: list[RegionResponse]


class ExhibitListParams(ApiModel):
    # 요청 이름은 필드명의 camelCase(startDate, countryCode, genreIds ...)다
    cursor: str | None = Field(default=None, max_length=CURSOR_MAX_LENGTH)
    sort: ExhibitListSort = ExhibitListSort.POPULAR
    size: PageSize = DEFAULT_PAGE_SIZE
    q: SearchText = None
    start_date: date | None = None
    end_date: date | None = None
    domestic: bool | None = None
    country_code: CountryCode = None
    region: list[str] | None = Field(default=None, max_length=MAX_FILTER_VALUE)
    genre_ids: list[int] | None = Field(default=None, max_length=MAX_FILTER_VALUE)
    style_ids: list[int] | None = Field(default=None, max_length=MAX_FILTER_VALUE)
