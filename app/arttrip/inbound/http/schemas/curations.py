from arttrip.inbound.http.schemas.base import ApiModel
from arttrip.inbound.http.schemas.exhibits import ExhibitSummaryResponse


class CurationDetailResponse(ApiModel):
    id: int
    title: str
    exhibits: list[ExhibitSummaryResponse]
    next_cursor: int | None
    has_next: bool


class CurationSummaryResponse(ApiModel):
    id: int
    title: str
    exhibits: list[ExhibitSummaryResponse]
