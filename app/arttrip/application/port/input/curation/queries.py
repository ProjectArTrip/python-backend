from dataclasses import dataclass


@dataclass(frozen=True)
class GetCurationQuery:
    user_id: int | None
    curation_id: int
    cursor: int | None
    size: int


@dataclass(frozen=True)
class PickCurationQuery:
    user_id: int | None
    domestic: bool | None
    country_code: str | None


@dataclass(frozen=True)
class SearchCurationsQuery:
    keyword: str | None
    active: bool | None
    page: int
    size: int
