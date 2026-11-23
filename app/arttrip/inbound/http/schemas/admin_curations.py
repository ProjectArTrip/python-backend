from datetime import date
from typing import Annotated, Final

from pydantic import Field

from arttrip.application.domain.curation.refresh_cycle import RefreshCycle
from arttrip.application.domain.curation.sort_type import SortType
from arttrip.application.domain.exhibit.exhibit_status import ExhibitStatus
from arttrip.inbound.http.schemas.base import ApiModel

TITLE_MAX_LENGTH: Final = 100
MAX_CURATION_EXHIBITS: Final = 100


class AdminCurationListItemResponse(ApiModel):
    curation_id: int
    title: str
    exhibit_count: int
    created_at: date
    visible_from: date
    visible_to: date
    active: bool


class AdminCurationExhibitResponse(ApiModel):
    exhibit_id: int
    title: str | None
    poster_url: str | None
    status: ExhibitStatus
    start_date: date | None
    end_date: date | None
    hall_name: str


class AdminCurationDetailResponse(ApiModel):
    curation_id: int
    title: str
    refresh_cycle: RefreshCycle
    sort_type: SortType
    visible_from: date
    visible_to: date
    active: bool
    exhibits: list[AdminCurationExhibitResponse]


class CurationFormRequest(ApiModel):
    title: str = Field(min_length=1, max_length=TITLE_MAX_LENGTH)
    refresh_cycle: RefreshCycle
    sort_type: SortType = SortType.NONE
    visible_from: date
    visible_to: date
    active: bool
    exhibit_ids: list[Annotated[int, Field(gt=0)]] = Field(
        min_length=1, max_length=MAX_CURATION_EXHIBITS
    )


class AdminCurationCreatedResponse(ApiModel):
    curation_id: int
