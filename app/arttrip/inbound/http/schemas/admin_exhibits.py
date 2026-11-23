from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Final, Literal

from pydantic import BeforeValidator, Field

from arttrip.application.domain.exhibit.exhibit_status import ExhibitStatus
from arttrip.application.port.input.exhibit.commands import CreateExhibitCommand
from arttrip.application.util.sort_direction import SortDirection
from arttrip.inbound.http.pagination import (
    DEFAULT_PAGE_SIZE,
    AdminPageSize,
    PageIndex,
)
from arttrip.inbound.http.query_params import SearchText
from arttrip.inbound.http.schemas.base import ApiModel, CaseInsensitive

DRAFT_VALUE_MAX_LENGTH: Final = 32767
DraftValue = Annotated[str | None, Field(max_length=DRAFT_VALUE_MAX_LENGTH)]
URL_PATTERN: Final = r"^https?://"
MAX_KEYWORDS: Final = 20


class ImportRowStatus(StrEnum):
    VALID = "VALID"
    INVALID = "INVALID"
    DUPLICATE = "DUPLICATE"


class AdminExhibitListItemResponse(ApiModel):
    exhibit_id: int
    title: str | None
    exhibit_period: str
    country: str
    region: str
    genres: list[str]
    status: ExhibitStatus
    hall_name: str


class AdminExhibitDetailResponse(ApiModel):
    exhibit_id: int
    title: str | None
    description: str | None
    poster_url: str | None
    ticket_url: str | None
    start_date: date | None
    end_date: date | None
    status: ExhibitStatus
    exhibit_hall_id: int
    exhibit_hall_name: str
    country: str
    region: str
    address: str | None
    opening_hours: str | None
    phone: str | None
    latitude: float
    longitude: float
    is_domestic: bool
    genres: list[str]
    styles: list[str]


def _empty_to_none(value: object) -> object:
    return None if value == "" else value


EmptyAsNone = BeforeValidator(_empty_to_none)


class ExhibitFormRequest(ApiModel):
    title: str = Field(min_length=1, max_length=255)
    description: Annotated[str | None, EmptyAsNone] = Field(
        default=None, max_length=10000
    )
    poster_url: Annotated[str | None, EmptyAsNone] = Field(
        default=None, max_length=1024, pattern=URL_PATTERN
    )
    ticket_url: Annotated[str | None, EmptyAsNone] = Field(
        default=None, max_length=1024, pattern=URL_PATTERN
    )
    start_date: Annotated[date | None, EmptyAsNone] = None
    end_date: Annotated[date | None, EmptyAsNone] = None
    status: ExhibitStatus | None = None
    exhibit_hall_name: str = Field(min_length=1, max_length=255)
    country: str = Field(min_length=1, max_length=255)
    region: str = Field(default="", max_length=255)
    address: Annotated[str | None, EmptyAsNone] = Field(default=None, max_length=255)
    opening_hours: Annotated[str | None, EmptyAsNone] = Field(
        default=None, max_length=500
    )
    phone: Annotated[str | None, EmptyAsNone] = Field(default=None, max_length=255)
    is_domestic: bool | None = None
    genres: list[str] = Field(default_factory=list, max_length=MAX_KEYWORDS)
    styles: list[str] = Field(default_factory=list, max_length=MAX_KEYWORDS)


class UpdateExhibitRequest(ExhibitFormRequest):
    latitude: Decimal | None = None
    longitude: Decimal | None = None


class CreateExhibitRequest(ExhibitFormRequest):
    latitude: Decimal
    longitude: Decimal
    exhibit_report_id: int | None = None

    def to_command(self) -> CreateExhibitCommand:
        return CreateExhibitCommand(
            title=self.title,
            description=self.description,
            poster_url=self.poster_url,
            ticket_url=self.ticket_url,
            start_date=self.start_date,
            end_date=self.end_date,
            hall_name=self.exhibit_hall_name,
            country_name=self.country,
            region=self.region,
            address=self.address,
            opening_hours=self.opening_hours,
            phone=self.phone,
            latitude=self.latitude,
            longitude=self.longitude,
            genre_names=frozenset(self.genres),
            style_names=frozenset(self.styles),
            is_domestic=self.is_domestic,
        )


class ExhibitDraftRow(ApiModel):
    row_number: int = Field(ge=1)
    title: DraftValue = None
    description: DraftValue = None
    poster_url: DraftValue = None
    ticket_url: DraftValue = None
    start_date: DraftValue = None
    end_date: DraftValue = None
    exhibit_hall_name: DraftValue = None
    country: DraftValue = None
    region: DraftValue = None
    address: DraftValue = None
    opening_hours: DraftValue = None
    phone: DraftValue = None
    latitude: DraftValue = None
    longitude: DraftValue = None
    genres: DraftValue = None
    styles: DraftValue = None


class ExhibitCreatedResponse(ApiModel):
    exhibit_id: int


class ExhibitDraftResponse(ApiModel):
    title: str
    description: str | None
    poster_url: str | None
    ticket_url: str | None
    start_date: date | None
    end_date: date | None
    exhibit_hall_name: str
    country: str
    region: str
    address: str | None
    opening_hours: str | None
    phone: str | None
    latitude: float
    longitude: float
    is_domestic: bool
    genres: list[str]
    styles: list[str]


class ExhibitImportErrorResponse(ApiModel):
    row: int
    field: str | None
    message: str


class ExhibitImportPreviewResponse(ApiModel):
    total_count: int
    rows: list[ExhibitImportPreviewRowResponse]
    duplicate_rows: list[int]
    errors: list[ExhibitImportErrorResponse]
    source_total_count: int | None = None


class ExhibitImportResponse(ApiModel):
    created_count: int
    exhibit_ids: list[int]
    skipped_count: int


class ExhibitImportPreviewRowResponse(ExhibitDraftRow):
    status: ImportRowStatus


class ExhibitImportRequest(ApiModel):
    rows: list[ExhibitDraftRow] = Field(min_length=1)


MAX_GENRE_FILTERS: Final = 20


class AdminExhibitSearchParams(ApiModel):
    page: PageIndex = 0
    size: AdminPageSize = DEFAULT_PAGE_SIZE
    sort: Literal["createdAt", "startDate", "endDate", "title"] = "createdAt"
    direction: Annotated[SortDirection, CaseInsensitive] = SortDirection.DESC
    keyword: SearchText = None
    status: list[ExhibitStatus] | None = Field(
        default=None, max_length=len(ExhibitStatus)
    )
    country: SearchText = None
    region: SearchText = None
    genre: list[str] | None = Field(default=None, max_length=MAX_GENRE_FILTERS)
    start_date: date | None = None
    end_date: date | None = None
